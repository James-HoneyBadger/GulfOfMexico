#pragma once

#include "lexer.h"
#include "ast.h"
#include <memory>
#include <vector>

namespace gom {

class Parser {
public:
    explicit Parser(std::vector<Token> tokens);
    
    std::unique_ptr<Program> parse();
    
private:
    std::vector<Token> tokens;
    size_t current;
    
    // Helpers
    Token peek(int offset = 0) const;
    Token advance();
    bool match(TokenType type);
    bool check(TokenType type) const;
    bool isAtEnd() const;
    void consume(TokenType type, const std::string& message);
    
    // Parsing methods
    std::unique_ptr<ASTNode> parseStatement();
    std::unique_ptr<ASTNode> parseVarDeclaration();
    std::unique_ptr<ASTNode> parseFunctionDef();
    std::unique_ptr<ASTNode> parseClassDef();
    std::unique_ptr<ASTNode> parseIfStatement();
    std::unique_ptr<ASTNode> parseReturnStatement();
    std::unique_ptr<ASTNode> parseExpressionStatement();
    std::unique_ptr<ASTNode> parseSatiricalStatement();
    std::unique_ptr<ASTNode> parseDeleteStatement();
    std::unique_ptr<ASTNode> parseReverseStatement();
    
    // Helper to check if token is a satirical keyword
    bool isSatiricalKeyword(TokenType type) const;
    
    // Expression parsing (precedence climbing)
    std::unique_ptr<ASTNode> parseExpression();
    std::unique_ptr<ASTNode> parseLogicalOr();
    std::unique_ptr<ASTNode> parseLogicalAnd();
    std::unique_ptr<ASTNode> parseEquality();
    std::unique_ptr<ASTNode> parseComparison();
    std::unique_ptr<ASTNode> parseAdditive();
    std::unique_ptr<ASTNode> parseMultiplicative();
    std::unique_ptr<ASTNode> parseUnary();
    std::unique_ptr<ASTNode> parsePostfix();
    std::unique_ptr<ASTNode> parsePrimary();
    
    std::vector<std::unique_ptr<ASTNode>> parseBlock();
    std::vector<std::string> parseParameterList();
    std::vector<std::unique_ptr<ASTNode>> parseArgumentList();
};

} // namespace gom
