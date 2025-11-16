#include "ast.h"

namespace gom {

std::string NumberLiteral::toString() const {
    return std::to_string(value);
}

std::string StringLiteral::toString() const {
    return "\"" + value + "\"";
}

std::string BoolLiteral::toString() const {
    return value ? "true" : "false";
}

std::string Identifier::toString() const {
    return name;
}

std::string BinaryOp::toString() const {
    return "(" + left->toString() + " " + op + " " + right->toString() + ")";
}

std::string UnaryOp::toString() const {
    return "(" + op + operand->toString() + ")";
}

std::string FunctionCall::toString() const {
    std::string result = name + "(";
    for (size_t i = 0; i < args.size(); i++) {
        result += args[i]->toString();
        if (i < args.size() - 1) result += ", ";
    }
    result += ")";
    return result;
}

std::string ArrayLiteral::toString() const {
    std::string result = "[";
    for (size_t i = 0; i < elements.size(); i++) {
        result += elements[i]->toString();
        if (i < elements.size() - 1) result += ", ";
    }
    result += "]";
    return result;
}

std::string IndexAccess::toString() const {
    return object->toString() + "[" + index->toString() + "]";
}

std::string VarDeclaration::toString() const {
    std::string result = isConst ? "const " : "var ";
    result += name;
    if (initializer) {
        result += " = " + initializer->toString();
    }
    return result;
}

std::string Assignment::toString() const {
    return name + " = " + value->toString();
}

std::string FunctionDef::toString() const {
    std::string result = isAsync ? "async function " : "function ";
    result += name + "(";
    for (size_t i = 0; i < params.size(); i++) {
        result += params[i];
        if (i < params.size() - 1) result += ", ";
    }
    result += ") => { ... }";
    return result;
}

std::string ClassDef::toString() const {
    return "class " + name + " { ... }";
}

std::string IfStatement::toString() const {
    return "if (" + condition->toString() + ") { ... }";
}

std::string ReturnStatement::toString() const {
    return "return " + (value ? value->toString() : "");
}

std::string Program::toString() const {
    std::string result = "Program:\n";
    for (const auto& stmt : statements) {
        result += "  " + stmt->toString() + "\n";
    }
    return result;
}

} // namespace gom
