#include "lexer.h"
#include "parser.h"
#include "codegen.h"
#include <iostream>
#include <fstream>
#include <sstream>

void printUsage(const char* progName) {
    std::cerr << "Usage: " << progName << " <input.gom> [-o output.cpp]\n";
    std::cerr << "\nGulf of Mexico Compiler\n";
    std::cerr << "Compiles .gom source files to C++\n\n";
    std::cerr << "Options:\n";
    std::cerr << "  -o <file>    Output file (default: a.cpp)\n";
    std::cerr << "  -h, --help   Show this help message\n";
}

std::string readFile(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        throw std::runtime_error("Could not open file: " + filename);
    }
    
    std::stringstream buffer;
    buffer << file.rdbuf();
    return buffer.str();
}

void writeFile(const std::string& filename, const std::string& content) {
    std::ofstream file(filename);
    if (!file.is_open()) {
        throw std::runtime_error("Could not write to file: " + filename);
    }
    file << content;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        printUsage(argv[0]);
        return 1;
    }
    
    std::string inputFile;
    std::string outputFile = "a.cpp";
    
    // Parse arguments
    for (int i = 1; i < argc; i++) {
        std::string arg = argv[i];
        if (arg == "-h" || arg == "--help") {
            printUsage(argv[0]);
            return 0;
        } else if (arg == "-o" && i + 1 < argc) {
            outputFile = argv[++i];
        } else if (arg[0] != '-') {
            inputFile = arg;
        } else {
            std::cerr << "Unknown option: " << arg << "\n";
            printUsage(argv[0]);
            return 1;
        }
    }
    
    if (inputFile.empty()) {
        std::cerr << "Error: No input file specified\n";
        printUsage(argv[0]);
        return 1;
    }
    
    try {
        std::cout << "Compiling " << inputFile << "...\n";
        
        // Read source
        std::string source = readFile(inputFile);
        
        // Lexical analysis
        gom::Lexer lexer(source);
        auto tokens = lexer.tokenize();
        std::cout << "Lexer: Generated " << tokens.size() << " tokens\n";
        
        // Parsing
        gom::Parser parser(tokens);
        auto ast = parser.parse();
        std::cout << "Parser: Built AST with " << ast->statements.size() << " statements\n";
        
        // Code generation
        gom::CodeGenerator codegen;
        std::string cppCode = codegen.generate(*ast);
        std::cout << "CodeGen: Generated C++ code\n";
        
        // Write output
        writeFile(outputFile, cppCode);
        std::cout << "Success: Written to " << outputFile << "\n";
        std::cout << "\nTo compile the output:\n";
        std::cout << "  g++ -std=c++17 " << outputFile << " -o program\n";
        std::cout << "  ./program\n";
        
        return 0;
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        return 1;
    }
}
