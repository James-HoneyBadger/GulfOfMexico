#pragma once

#include <memory>
#include <string>
#include <vector>
#include <variant>
#include <optional>

namespace gom {

// Forward declarations
class ASTNode;
class Expression;
class Statement;

// Base AST node
class ASTNode {
public:
    virtual ~ASTNode() = default;
    virtual std::string toString() const = 0;
};

// Expression types
class NumberLiteral : public ASTNode {
public:
    double value;
    explicit NumberLiteral(double v) : value(v) {}
    std::string toString() const override;
};

class StringLiteral : public ASTNode {
public:
    std::string value;
    explicit StringLiteral(std::string v) : value(std::move(v)) {}
    std::string toString() const override;
};

class BoolLiteral : public ASTNode {
public:
    bool value;
    explicit BoolLiteral(bool v) : value(v) {}
    std::string toString() const override;
};

class Identifier : public ASTNode {
public:
    std::string name;
    explicit Identifier(std::string n) : name(std::move(n)) {}
    std::string toString() const override;
};

class BinaryOp : public ASTNode {
public:
    std::string op;
    std::unique_ptr<ASTNode> left;
    std::unique_ptr<ASTNode> right;

    BinaryOp(std::string o, std::unique_ptr<ASTNode> l, std::unique_ptr<ASTNode> r)
        : op(std::move(o)), left(std::move(l)), right(std::move(r)) {}
    std::string toString() const override;
};

class UnaryOp : public ASTNode {
public:
    std::string op;
    std::unique_ptr<ASTNode> operand;

    UnaryOp(std::string o, std::unique_ptr<ASTNode> opnd)
        : op(std::move(o)), operand(std::move(opnd)) {}
    std::string toString() const override;
};

class FunctionCall : public ASTNode {
public:
    std::string name;
    std::vector<std::unique_ptr<ASTNode>> args;

    FunctionCall(std::string n, std::vector<std::unique_ptr<ASTNode>> a)
        : name(std::move(n)), args(std::move(a)) {}
    std::string toString() const override;
};

class ArrayLiteral : public ASTNode {
public:
    std::vector<std::unique_ptr<ASTNode>> elements;

    explicit ArrayLiteral(std::vector<std::unique_ptr<ASTNode>> e)
        : elements(std::move(e)) {}
    std::string toString() const override;
};

class IndexAccess : public ASTNode {
public:
    std::unique_ptr<ASTNode> object;
    std::unique_ptr<ASTNode> index;

    IndexAccess(std::unique_ptr<ASTNode> obj, std::unique_ptr<ASTNode> idx)
        : object(std::move(obj)), index(std::move(idx)) {}
    std::string toString() const override;
};

// Statement types
class VarDeclaration : public ASTNode {
public:
    std::string name;
    bool isConst;
    std::unique_ptr<ASTNode> initializer;
    std::optional<double> lifetime; // For temporal lifetimes

    VarDeclaration(std::string n, bool c, std::unique_ptr<ASTNode> init)
        : name(std::move(n)), isConst(c), initializer(std::move(init)) {}
    std::string toString() const override;
};

class Assignment : public ASTNode {
public:
    std::string name;
    std::unique_ptr<ASTNode> value;

    Assignment(std::string n, std::unique_ptr<ASTNode> v)
        : name(std::move(n)), value(std::move(v)) {}
    std::string toString() const override;
};

class FunctionDef : public ASTNode {
public:
    std::string name;
    std::vector<std::string> params;
    std::vector<std::unique_ptr<ASTNode>> body;
    bool isAsync;

    FunctionDef(std::string n, std::vector<std::string> p,
                std::vector<std::unique_ptr<ASTNode>> b, bool async)
        : name(std::move(n)), params(std::move(p)), body(std::move(b)), isAsync(async) {}
    std::string toString() const override;
};

class ClassDef : public ASTNode {
public:
    std::string name;
    std::vector<std::unique_ptr<ASTNode>> members;

    ClassDef(std::string n, std::vector<std::unique_ptr<ASTNode>> m)
        : name(std::move(n)), members(std::move(m)) {}
    std::string toString() const override;
};

class IfStatement : public ASTNode {
public:
    std::unique_ptr<ASTNode> condition;
    std::vector<std::unique_ptr<ASTNode>> thenBranch;
    std::vector<std::unique_ptr<ASTNode>> elseBranch;

    IfStatement(std::unique_ptr<ASTNode> cond,
                std::vector<std::unique_ptr<ASTNode>> thenB,
                std::vector<std::unique_ptr<ASTNode>> elseB)
        : condition(std::move(cond)), thenBranch(std::move(thenB)),
          elseBranch(std::move(elseB)) {}
    std::string toString() const override;
};

class ReturnStatement : public ASTNode {
public:
    std::unique_ptr<ASTNode> value;

    explicit ReturnStatement(std::unique_ptr<ASTNode> v)
        : value(std::move(v)) {}
    std::string toString() const override;
};

class Program : public ASTNode {
public:
    std::vector<std::unique_ptr<ASTNode>> statements;

    explicit Program(std::vector<std::unique_ptr<ASTNode>> stmts)
        : statements(std::move(stmts)) {}
    std::string toString() const override;
};

// Satirical statement types
class SatiricalStatement : public ASTNode {
public:
    std::string keyword;
    std::vector<std::unique_ptr<ASTNode>> body;

    SatiricalStatement(std::string kw, std::vector<std::unique_ptr<ASTNode>> b)
        : keyword(std::move(kw)), body(std::move(b)) {}
    std::string toString() const override;
};

class DeleteStatement : public ASTNode {
public:
    std::string name;

    explicit DeleteStatement(std::string n) : name(std::move(n)) {}
    std::string toString() const override;
};

class ReverseStatement : public ASTNode {
public:
    std::string name;

    explicit ReverseStatement(std::string n) : name(std::move(n)) {}
    std::string toString() const override;
};

} // namespace gom
