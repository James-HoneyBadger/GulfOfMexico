#pragma once

#include "ast.h"
#include <string>
#include <sstream>
#include <unordered_map>

namespace gom {

class CodeGenerator {
public:
    CodeGenerator();
    
    std::string generate(const Program& program);
    
private:
    std::stringstream code;
    int indentLevel;
    std::unordered_map<std::string, std::string> symbolTable;
    
    void indent();
    void emit(const std::string& str);
    void emitLine(const std::string& str);
    
    void generateNode(const ASTNode* node);
    void generateStatement(const ASTNode* node);
    void generateExpression(const ASTNode* node);
    
    void generateVarDeclaration(const VarDeclaration* node);
    void generateAssignment(const Assignment* node);
    void generateFunctionDef(const FunctionDef* node);
    void generateClassDef(const ClassDef* node);
    void generateIfStatement(const IfStatement* node);
    void generateReturnStatement(const ReturnStatement* node);
    void generateSatiricalStatement(const SatiricalStatement* node);
    void generateDeleteStatement(const DeleteStatement* node);
    void generateReverseStatement(const ReverseStatement* node);
    
    void generateBinaryOp(const BinaryOp* node);
    void generateUnaryOp(const UnaryOp* node);
    void generateFunctionCall(const FunctionCall* node);
    void generateArrayLiteral(const ArrayLiteral* node);
    void generateIndexAccess(const IndexAccess* node);
    
    std::string generateRuntimeIncludes();
    std::string generateRuntimeCode();
};

} // namespace gom
