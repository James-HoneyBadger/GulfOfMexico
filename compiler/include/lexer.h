#pragma once

#include <string>
#include <vector>
#include <optional>

namespace gom {

enum class TokenType {
    // Literals
    NUMBER,
    STRING,
    BOOL_TRUE,
    BOOL_FALSE,
    UNDEFINED,
    
    // Identifiers and keywords
    IDENTIFIER,
    FUNCTION,
    FN,
    ASYNC,
    CLASS,
    VAR,
    CONST,
    RETURN,
    IF,
    WHEN,
    AFTER,
    NEW,
    DELETE,
    IMPORT,
    EXPORT,
    FROM,
    AWAIT,
    NEXT,
    PREVIOUS,
    
    // Operators
    PLUS,
    MINUS,
    STAR,
    SLASH,
    PERCENT,
    EQUALS,
    DOUBLE_EQUALS,
    NOT_EQUALS,
    APPROX_EQUALS,
    LESS_THAN,
    GREATER_THAN,
    LESS_EQUAL,
    GREATER_EQUAL,
    AND,
    OR,
    NOT,
    BANG,
    
    // Delimiters
    LPAREN,
    RPAREN,
    LBRACE,
    RBRACE,
    LBRACKET,
    RBRACKET,
    LANGLE,
    RANGLE,
    COMMA,
    DOT,
    ARROW,
    DOUBLE_ARROW,
    COLON,
    
    // Special
    NEWLINE,
    EOF_TOKEN,
    INVALID
};

struct Token {
    TokenType type;
    std::string value;
    int line;
    int column;
    
    Token(TokenType t, std::string v, int l, int c)
        : type(t), value(std::move(v)), line(l), column(c) {}
};

class Lexer {
public:
    explicit Lexer(std::string source);
    
    std::vector<Token> tokenize();
    Token nextToken();
    
private:
    std::string source;
    size_t pos;
    int line;
    int column;
    
    char peek(int offset = 0) const;
    char advance();
    void skipWhitespace();
    void skipComment();
    
    Token tokenizeNumber();
    Token tokenizeString();
    Token tokenizeIdentifierOrKeyword();
    Token tokenizeOperator();
    
    bool isDigit(char c) const;
    bool isAlpha(char c) const;
    bool isAlphaNumeric(char c) const;
    bool isAtEnd() const;
};

} // namespace gom
