#include "lexer.h"
#include <cctype>
#include <stdexcept>
#include <unordered_map>

namespace gom {

static std::unordered_map<std::string, TokenType> keywords = {
    {"function", TokenType::FUNCTION},
    {"fn", TokenType::FN},
    {"async", TokenType::ASYNC},
    {"class", TokenType::CLASS},
    {"var", TokenType::VAR},
    {"const", TokenType::CONST},
    {"return", TokenType::RETURN},
    {"if", TokenType::IF},
    {"when", TokenType::WHEN},
    {"after", TokenType::AFTER},
    {"new", TokenType::NEW},
    {"delete", TokenType::DELETE},
    {"import", TokenType::IMPORT},
    {"export", TokenType::EXPORT},
    {"from", TokenType::FROM},
    {"await", TokenType::AWAIT},
    {"next", TokenType::NEXT},
    {"previous", TokenType::PREVIOUS},
    {"true", TokenType::BOOL_TRUE},
    {"false", TokenType::BOOL_FALSE},
    {"undefined", TokenType::UNDEFINED},
};

Lexer::Lexer(std::string src)
    : source(std::move(src)), pos(0), line(1), column(1) {}

std::vector<Token> Lexer::tokenize() {
    std::vector<Token> tokens;
    while (!isAtEnd()) {
        Token tok = nextToken();
        if (tok.type != TokenType::INVALID) {
            tokens.push_back(tok);
        }
    }
    tokens.emplace_back(TokenType::EOF_TOKEN, "", line, column);
    return tokens;
}

Token Lexer::nextToken() {
    skipWhitespace();
    
    if (isAtEnd()) {
        return Token(TokenType::EOF_TOKEN, "", line, column);
    }
    
    int startLine = line;
    int startCol = column;
    char c = peek();
    
    // Comments
    if (c == '/' && peek(1) == '/') {
        skipComment();
        return nextToken();
    }
    
    // Numbers
    if (isDigit(c)) {
        return tokenizeNumber();
    }
    
    // Strings
    if (c == '"' || c == '\'' || c == '`') {
        return tokenizeString();
    }
    
    // Identifiers and keywords
    if (isAlpha(c) || c == '_') {
        return tokenizeIdentifierOrKeyword();
    }
    
    // Operators and delimiters
    return tokenizeOperator();
}

char Lexer::peek(int offset) const {
    if (pos + offset >= source.length()) {
        return '\0';
    }
    return source[pos + offset];
}

char Lexer::advance() {
    if (isAtEnd()) return '\0';
    
    char c = source[pos++];
    if (c == '\n') {
        line++;
        column = 1;
    } else {
        column++;
    }
    return c;
}

void Lexer::skipWhitespace() {
    while (!isAtEnd()) {
        char c = peek();
        if (c == ' ' || c == '\t' || c == '\r') {
            advance();
        } else if (c == '\n') {
            // Newlines are significant in GOM but we'll handle them as whitespace for now
            advance();
        } else {
            break;
        }
    }
}

void Lexer::skipComment() {
    while (!isAtEnd() && peek() != '\n') {
        advance();
    }
}

Token Lexer::tokenizeNumber() {
    int startLine = line;
    int startCol = column;
    std::string value;
    
    while (isDigit(peek())) {
        value += advance();
    }
    
    if (peek() == '.' && isDigit(peek(1))) {
        value += advance(); // consume '.'
        while (isDigit(peek())) {
            value += advance();
        }
    }
    
    return Token(TokenType::NUMBER, value, startLine, startCol);
}

Token Lexer::tokenizeString() {
    int startLine = line;
    int startCol = column;
    char quote = advance(); // consume opening quote
    std::string value;
    
    while (!isAtEnd() && peek() != quote) {
        if (peek() == '\\') {
            advance(); // consume backslash
            if (!isAtEnd()) {
                char escaped = advance();
                switch (escaped) {
                    case 'n': value += '\n'; break;
                    case 't': value += '\t'; break;
                    case 'r': value += '\r'; break;
                    case '\\': value += '\\'; break;
                    case '"': value += '"'; break;
                    case '\'': value += '\''; break;
                    default: value += escaped; break;
                }
            }
        } else {
            value += advance();
        }
    }
    
    if (!isAtEnd()) {
        advance(); // consume closing quote
    }
    
    return Token(TokenType::STRING, value, startLine, startCol);
}

Token Lexer::tokenizeIdentifierOrKeyword() {
    int startLine = line;
    int startCol = column;
    std::string value;
    
    while (isAlphaNumeric(peek()) || peek() == '_') {
        value += advance();
    }
    
    auto it = keywords.find(value);
    if (it != keywords.end()) {
        return Token(it->second, value, startLine, startCol);
    }
    
    return Token(TokenType::IDENTIFIER, value, startLine, startCol);
}

Token Lexer::tokenizeOperator() {
    int startLine = line;
    int startCol = column;
    char c = advance();
    
    switch (c) {
        case '+': return Token(TokenType::PLUS, "+", startLine, startCol);
        case '-': return Token(TokenType::MINUS, "-", startLine, startCol);
        case '*': return Token(TokenType::STAR, "*", startLine, startCol);
        case '/': return Token(TokenType::SLASH, "/", startLine, startCol);
        case '%': return Token(TokenType::PERCENT, "%", startLine, startCol);
        case '!':
            if (peek() == '=') {
                advance();
                return Token(TokenType::NOT_EQUALS, "!=", startLine, startCol);
            }
            return Token(TokenType::BANG, "!", startLine, startCol);
        case '=':
            if (peek() == '=') {
                advance();
                return Token(TokenType::DOUBLE_EQUALS, "==", startLine, startCol);
            }
            if (peek() == '>') {
                advance();
                return Token(TokenType::DOUBLE_ARROW, "=>", startLine, startCol);
            }
            return Token(TokenType::EQUALS, "=", startLine, startCol);
        case '<':
            if (peek() == '=') {
                advance();
                return Token(TokenType::LESS_EQUAL, "<=", startLine, startCol);
            }
            return Token(TokenType::LESS_THAN, "<", startLine, startCol);
        case '>':
            if (peek() == '=') {
                advance();
                return Token(TokenType::GREATER_EQUAL, ">=", startLine, startCol);
            }
            return Token(TokenType::GREATER_THAN, ">", startLine, startCol);
        case '~':
            if (peek() == '=') {
                advance();
                return Token(TokenType::APPROX_EQUALS, "~=", startLine, startCol);
            }
            return Token(TokenType::INVALID, "~", startLine, startCol);
        case '&':
            if (peek() == '&') {
                advance();
                return Token(TokenType::AND, "&&", startLine, startCol);
            }
            return Token(TokenType::INVALID, "&", startLine, startCol);
        case '|':
            if (peek() == '|') {
                advance();
                return Token(TokenType::OR, "||", startLine, startCol);
            }
            return Token(TokenType::INVALID, "|", startLine, startCol);
        case '(': return Token(TokenType::LPAREN, "(", startLine, startCol);
        case ')': return Token(TokenType::RPAREN, ")", startLine, startCol);
        case '{': return Token(TokenType::LBRACE, "{", startLine, startCol);
        case '}': return Token(TokenType::RBRACE, "}", startLine, startCol);
        case '[': return Token(TokenType::LBRACKET, "[", startLine, startCol);
        case ']': return Token(TokenType::RBRACKET, "]", startLine, startCol);
        case ',': return Token(TokenType::COMMA, ",", startLine, startCol);
        case '.': return Token(TokenType::DOT, ".", startLine, startCol);
        case ':': return Token(TokenType::COLON, ":", startLine, startCol);
        default:
            return Token(TokenType::INVALID, std::string(1, c), startLine, startCol);
    }
}

bool Lexer::isDigit(char c) const {
    return c >= '0' && c <= '9';
}

bool Lexer::isAlpha(char c) const {
    return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z');
}

bool Lexer::isAlphaNumeric(char c) const {
    return isAlpha(c) || isDigit(c);
}

bool Lexer::isAtEnd() const {
    return pos >= source.length();
}

} // namespace gom
