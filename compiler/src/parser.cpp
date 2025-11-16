#include "parser.h"
#include <stdexcept>

namespace gom {

Parser::Parser(std::vector<Token> toks)
    : tokens(std::move(toks)), current(0) {}

std::unique_ptr<Program> Parser::parse() {
    std::vector<std::unique_ptr<ASTNode>> statements;
    
    while (!isAtEnd()) {
        auto stmt = parseStatement();
        if (stmt) {
            statements.push_back(std::move(stmt));
        }
    }
    
    return std::make_unique<Program>(std::move(statements));
}

Token Parser::peek(int offset) const {
    size_t idx = current + offset;
    if (idx >= tokens.size()) {
        return tokens.back();
    }
    return tokens[idx];
}

Token Parser::advance() {
    if (!isAtEnd()) {
        current++;
    }
    return tokens[current - 1];
}

bool Parser::match(TokenType type) {
    if (check(type)) {
        advance();
        return true;
    }
    return false;
}

bool Parser::check(TokenType type) const {
    if (isAtEnd()) return false;
    return peek().type == type;
}

bool Parser::isAtEnd() const {
    return peek().type == TokenType::EOF_TOKEN;
}

void Parser::consume(TokenType type, const std::string& message) {
    if (check(type)) {
        advance();
        return;
    }
    throw std::runtime_error(message + " at line " + std::to_string(peek().line));
}

std::unique_ptr<ASTNode> Parser::parseStatement() {
    // Skip bangs (statement terminators)
    while (match(TokenType::BANG)) {}
    
    if (check(TokenType::VAR) || check(TokenType::CONST)) {
        return parseVarDeclaration();
    }
    if (check(TokenType::FUNCTION) || check(TokenType::FN) || check(TokenType::ASYNC)) {
        return parseFunctionDef();
    }
    if (check(TokenType::CLASS)) {
        return parseClassDef();
    }
    if (check(TokenType::IF)) {
        return parseIfStatement();
    }
    if (check(TokenType::RETURN)) {
        return parseReturnStatement();
    }
    
    return parseExpressionStatement();
}

std::unique_ptr<ASTNode> Parser::parseVarDeclaration() {
    bool isConst = false;
    
    // Handle "const", "var", "const var", "const const const"
    while (match(TokenType::CONST)) {
        isConst = true;
    }
    match(TokenType::VAR); // optional after const
    
    consume(TokenType::IDENTIFIER, "Expected variable name");
    std::string name = tokens[current - 1].value;
    
    std::unique_ptr<ASTNode> init = nullptr;
    if (match(TokenType::EQUALS)) {
        init = parseExpression();
    }
    
    match(TokenType::BANG); // optional statement terminator
    
    return std::make_unique<VarDeclaration>(name, isConst, std::move(init));
}

std::unique_ptr<ASTNode> Parser::parseFunctionDef() {
    bool isAsync = match(TokenType::ASYNC);
    
    if (!match(TokenType::FUNCTION)) {
        match(TokenType::FN);
    }
    
    consume(TokenType::IDENTIFIER, "Expected function name");
    std::string name = tokens[current - 1].value;
    
    std::vector<std::string> params;
    if (match(TokenType::LPAREN)) {
        params = parseParameterList();
        consume(TokenType::RPAREN, "Expected ')' after parameters");
    }
    
    consume(TokenType::DOUBLE_ARROW, "Expected '=>' after function signature");
    
    std::vector<std::unique_ptr<ASTNode>> body;
    if (match(TokenType::LBRACE)) {
        body = parseBlock();
        consume(TokenType::RBRACE, "Expected '}' after function body");
    } else {
        // Single expression body
        body.push_back(std::make_unique<ReturnStatement>(parseExpression()));
    }
    
    match(TokenType::BANG);
    
    return std::make_unique<FunctionDef>(name, params, std::move(body), isAsync);
}

std::unique_ptr<ASTNode> Parser::parseClassDef() {
    consume(TokenType::CLASS, "Expected 'class'");
    consume(TokenType::IDENTIFIER, "Expected class name");
    std::string name = tokens[current - 1].value;
    
    consume(TokenType::LBRACE, "Expected '{' after class name");
    
    std::vector<std::unique_ptr<ASTNode>> members;
    while (!check(TokenType::RBRACE) && !isAtEnd()) {
        members.push_back(parseStatement());
    }
    
    consume(TokenType::RBRACE, "Expected '}' after class body");
    match(TokenType::BANG);
    
    return std::make_unique<ClassDef>(name, std::move(members));
}

std::unique_ptr<ASTNode> Parser::parseIfStatement() {
    consume(TokenType::IF, "Expected 'if'");
    
    auto condition = parseExpression();
    
    consume(TokenType::LBRACE, "Expected '{' after if condition");
    auto thenBranch = parseBlock();
    consume(TokenType::RBRACE, "Expected '}' after if body");
    
    std::vector<std::unique_ptr<ASTNode>> elseBranch;
    // Note: GOM doesn't have else keyword in spec, but we can extend
    
    return std::make_unique<IfStatement>(std::move(condition),
                                          std::move(thenBranch),
                                          std::move(elseBranch));
}

std::unique_ptr<ASTNode> Parser::parseReturnStatement() {
    consume(TokenType::RETURN, "Expected 'return'");
    
    auto value = parseExpression();
    match(TokenType::BANG);
    
    return std::make_unique<ReturnStatement>(std::move(value));
}

std::unique_ptr<ASTNode> Parser::parseExpressionStatement() {
    auto expr = parseExpression();
    match(TokenType::BANG);
    return expr;
}

std::unique_ptr<ASTNode> Parser::parseExpression() {
    return parseLogicalOr();
}

std::unique_ptr<ASTNode> Parser::parseLogicalOr() {
    auto left = parseLogicalAnd();
    
    while (match(TokenType::OR)) {
        left = std::make_unique<BinaryOp>("||", std::move(left), parseLogicalAnd());
    }
    
    return left;
}

std::unique_ptr<ASTNode> Parser::parseLogicalAnd() {
    auto left = parseEquality();
    
    while (match(TokenType::AND)) {
        left = std::make_unique<BinaryOp>("&&", std::move(left), parseEquality());
    }
    
    return left;
}

std::unique_ptr<ASTNode> Parser::parseEquality() {
    auto left = parseComparison();
    
    while (true) {
        if (match(TokenType::DOUBLE_EQUALS)) {
            left = std::make_unique<BinaryOp>("==", std::move(left), parseComparison());
        } else if (match(TokenType::NOT_EQUALS)) {
            left = std::make_unique<BinaryOp>("!=", std::move(left), parseComparison());
        } else if (match(TokenType::APPROX_EQUALS)) {
            left = std::make_unique<BinaryOp>("~=", std::move(left), parseComparison());
        } else {
            break;
        }
    }
    
    return left;
}

std::unique_ptr<ASTNode> Parser::parseComparison() {
    auto left = parseAdditive();
    
    while (true) {
        if (match(TokenType::LESS_THAN)) {
            left = std::make_unique<BinaryOp>("<", std::move(left), parseAdditive());
        } else if (match(TokenType::GREATER_THAN)) {
            left = std::make_unique<BinaryOp>(">", std::move(left), parseAdditive());
        } else if (match(TokenType::LESS_EQUAL)) {
            left = std::make_unique<BinaryOp>("<=", std::move(left), parseAdditive());
        } else if (match(TokenType::GREATER_EQUAL)) {
            left = std::make_unique<BinaryOp>(">=", std::move(left), parseAdditive());
        } else {
            break;
        }
    }
    
    return left;
}

std::unique_ptr<ASTNode> Parser::parseAdditive() {
    auto left = parseMultiplicative();
    
    while (true) {
        if (match(TokenType::PLUS)) {
            left = std::make_unique<BinaryOp>("+", std::move(left), parseMultiplicative());
        } else if (match(TokenType::MINUS)) {
            left = std::make_unique<BinaryOp>("-", std::move(left), parseMultiplicative());
        } else {
            break;
        }
    }
    
    return left;
}

std::unique_ptr<ASTNode> Parser::parseMultiplicative() {
    auto left = parseUnary();
    
    while (true) {
        if (match(TokenType::STAR)) {
            left = std::make_unique<BinaryOp>("*", std::move(left), parseUnary());
        } else if (match(TokenType::SLASH)) {
            left = std::make_unique<BinaryOp>("/", std::move(left), parseUnary());
        } else if (match(TokenType::PERCENT)) {
            left = std::make_unique<BinaryOp>("%", std::move(left), parseUnary());
        } else {
            break;
        }
    }
    
    return left;
}

std::unique_ptr<ASTNode> Parser::parseUnary() {
    if (match(TokenType::MINUS)) {
        return std::make_unique<UnaryOp>("-", parseUnary());
    }
    if (match(TokenType::NOT)) {
        return std::make_unique<UnaryOp>("!", parseUnary());
    }
    
    return parsePostfix();
}

std::unique_ptr<ASTNode> Parser::parsePostfix() {
    auto expr = parsePrimary();
    
    while (true) {
        if (match(TokenType::LPAREN)) {
            // Function call
            auto args = parseArgumentList();
            consume(TokenType::RPAREN, "Expected ')' after arguments");
            
            if (auto* ident = dynamic_cast<Identifier*>(expr.get())) {
                expr = std::make_unique<FunctionCall>(ident->name, std::move(args));
            }
        } else if (match(TokenType::LBRACKET)) {
            // Array indexing
            auto index = parseExpression();
            consume(TokenType::RBRACKET, "Expected ']' after index");
            expr = std::make_unique<IndexAccess>(std::move(expr), std::move(index));
        } else if (match(TokenType::DOT)) {
            // Member access - treat as property lookup for now
            consume(TokenType::IDENTIFIER, "Expected property name after '.'");
            std::string prop = tokens[current - 1].value;
            expr = std::make_unique<IndexAccess>(std::move(expr),
                                                  std::make_unique<StringLiteral>(prop));
        } else {
            break;
        }
    }
    
    return expr;
}

std::unique_ptr<ASTNode> Parser::parsePrimary() {
    if (match(TokenType::NUMBER)) {
        double value = std::stod(tokens[current - 1].value);
        return std::make_unique<NumberLiteral>(value);
    }
    
    if (match(TokenType::STRING)) {
        return std::make_unique<StringLiteral>(tokens[current - 1].value);
    }
    
    if (match(TokenType::BOOL_TRUE)) {
        return std::make_unique<BoolLiteral>(true);
    }
    
    if (match(TokenType::BOOL_FALSE)) {
        return std::make_unique<BoolLiteral>(false);
    }
    
    if (match(TokenType::IDENTIFIER)) {
        return std::make_unique<Identifier>(tokens[current - 1].value);
    }
    
    if (match(TokenType::LBRACKET)) {
        std::vector<std::unique_ptr<ASTNode>> elements;
        if (!check(TokenType::RBRACKET)) {
            do {
                elements.push_back(parseExpression());
            } while (match(TokenType::COMMA));
        }
        consume(TokenType::RBRACKET, "Expected ']' after array literal");
        return std::make_unique<ArrayLiteral>(std::move(elements));
    }
    
    if (match(TokenType::LPAREN)) {
        auto expr = parseExpression();
        consume(TokenType::RPAREN, "Expected ')' after expression");
        return expr;
    }
    
    throw std::runtime_error("Unexpected token at line " + std::to_string(peek().line));
}

std::vector<std::unique_ptr<ASTNode>> Parser::parseBlock() {
    std::vector<std::unique_ptr<ASTNode>> statements;
    
    while (!check(TokenType::RBRACE) && !isAtEnd()) {
        statements.push_back(parseStatement());
    }
    
    return statements;
}

std::vector<std::string> Parser::parseParameterList() {
    std::vector<std::string> params;
    
    if (!check(TokenType::RPAREN)) {
        do {
            consume(TokenType::IDENTIFIER, "Expected parameter name");
            params.push_back(tokens[current - 1].value);
        } while (match(TokenType::COMMA));
    }
    
    return params;
}

std::vector<std::unique_ptr<ASTNode>> Parser::parseArgumentList() {
    std::vector<std::unique_ptr<ASTNode>> args;
    
    if (!check(TokenType::RPAREN)) {
        do {
            args.push_back(parseExpression());
        } while (match(TokenType::COMMA));
    }
    
    return args;
}

} // namespace gom
