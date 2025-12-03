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
    MAYBE,

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
    REVERSE,
    IMPORT,
    EXPORT,
    FROM,
    AWAIT,
    NEXT,
    PREVIOUS,

    // Try/Whatever
    TRY,
    WHATEVER,

    // Procrastination
    LATER,
    EVENTUALLY,
    WHENEVER,

    // Corporate Speak
    SYNERGIZE,
    LEVERAGE,
    PARADIGM_SHIFT,
    CIRCLE_BACK,
    TOUCH_BASE,

    // Emotional
    HAPPY,
    SAD,
    ANGRY,
    EXCITED,
    TIRED,

    // Superstitious
    LUCKY,
    UNLUCKY,
    CROSS_FINGERS,
    KNOCK_ON_WOOD,

    // Quantum
    QUANTUM,

    // Time Travel
    TIME_TRAVEL,

    // Gaslighting
    DEFINITELY_NOT,

    // Blockchain
    BLOCKCHAIN,
    SMART_CONTRACT,
    MINE,
    IMMUTABLE_LEDGER,
    TOKEN,
    NFT,
    WEB3,
    DAO,
    DEFI,
    HODL,

    // AI Buzzwords
    AI_POWERED,
    DEEP_LEARNING,
    NEURAL_NETWORK,
    MACHINE_LEARNING,

    // Agile
    SPRINT,
    STANDUP,
    RETRO,
    BURNDOWN,

    // Security Theater
    PENETRATION_TEST,
    VULNERABILITY_SCAN,
    SECURITY_AUDIT,
    COMPLIANCE_CHECK,

    // DevOps
    CONTAINERIZE,
    ORCHESTRATE,
    MICROSERVICE,
    KUBERNETES,

    // Startup
    PIVOT,
    DISRUPT,
    UNICORN,
    HOCKEY_STICK,

    // Built-in functions
    NUMBER_FUNC,
    STRING_FUNC,
    BOOLEAN_FUNC,
    MAP_FUNC,
    SIN,
    COS,
    TAN,
    SQRT,
    ABS,
    FLOOR,
    CEIL,
    ROUND,
    LOG,
    LOG10,
    EXP,
    POW,
    MEAN,
    MEDIAN,
    STDEV,
    VARIANCE,
    MIN_VAL,
    MAX_VAL,
    SUM_LIST,
    COMPOUND_INTEREST,
    SIMPLE_INTEREST,
    PMT,
    ROI,
    PROFIT_MARGIN,
    CAGR,
    LINEAR_REGRESSION,
    QUADRATIC_SOLVE,

    // Operators
    PLUS,
    MINUS,
    STAR,
    SLASH,
    PERCENT,
    EQUALS,
    DOUBLE_EQUALS,
    TRIPLE_EQUALS,
    QUAD_EQUALS,
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
