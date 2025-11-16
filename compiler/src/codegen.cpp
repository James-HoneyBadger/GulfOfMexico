#include "codegen.h"
#include <iostream>

namespace gom {

CodeGenerator::CodeGenerator() : indentLevel(0) {}

std::string CodeGenerator::generate(const Program& program) {
    code.str("");
    code.clear();
    
    // Generate includes and runtime
    emit(generateRuntimeIncludes());
    emit("\n");
    emit(generateRuntimeCode());
    emit("\n");
    
    // Generate main function start
    emitLine("int main() {");
    indentLevel++;
    
    // Generate all statements
    for (const auto& stmt : program.statements) {
        generateNode(stmt.get());
    }
    
    // Generate main function end
    indentLevel--;
    emitLine("}");
    
    return code.str();
}

void CodeGenerator::indent() {
    for (int i = 0; i < indentLevel; i++) {
        code << "    ";
    }
}

void CodeGenerator::emit(const std::string& str) {
    code << str;
}

void CodeGenerator::emitLine(const std::string& str) {
    indent();
    code << str << "\n";
}

void CodeGenerator::generateNode(const ASTNode* node) {
    if (auto* varDecl = dynamic_cast<const VarDeclaration*>(node)) {
        generateVarDeclaration(varDecl);
    } else if (auto* funcDef = dynamic_cast<const FunctionDef*>(node)) {
        generateFunctionDef(funcDef);
    } else if (auto* classDef = dynamic_cast<const ClassDef*>(node)) {
        generateClassDef(classDef);
    } else if (auto* ifStmt = dynamic_cast<const IfStatement*>(node)) {
        generateIfStatement(ifStmt);
    } else if (auto* retStmt = dynamic_cast<const ReturnStatement*>(node)) {
        generateReturnStatement(retStmt);
    } else {
        // Expression statement (including function calls like print)
        indent();
        generateExpression(node);
        emit(";\n");
    }
}

void CodeGenerator::generateStatement(const ASTNode* node) {
    generateNode(node);
}

void CodeGenerator::generateExpression(const ASTNode* node) {
    if (auto* num = dynamic_cast<const NumberLiteral*>(node)) {
        emit("GomValue(" + std::to_string(num->value) + ")");
    } else if (auto* str = dynamic_cast<const StringLiteral*>(node)) {
        emit("GomValue(std::string(\"" + str->value + "\"))");
    } else if (auto* boolLit = dynamic_cast<const BoolLiteral*>(node)) {
        emit("GomValue(" + std::string(boolLit->value ? "true" : "false") + ")");
    } else if (auto* ident = dynamic_cast<const Identifier*>(node)) {
        emit(ident->name);
    } else if (auto* binOp = dynamic_cast<const BinaryOp*>(node)) {
        generateBinaryOp(binOp);
    } else if (auto* unOp = dynamic_cast<const UnaryOp*>(node)) {
        generateUnaryOp(unOp);
    } else if (auto* funcCall = dynamic_cast<const FunctionCall*>(node)) {
        generateFunctionCall(funcCall);
    } else if (auto* arrLit = dynamic_cast<const ArrayLiteral*>(node)) {
        generateArrayLiteral(arrLit);
    } else if (auto* idxAccess = dynamic_cast<const IndexAccess*>(node)) {
        generateIndexAccess(idxAccess);
    }
}

void CodeGenerator::generateVarDeclaration(const VarDeclaration* node) {
    indent();
    if (node->isConst) {
        emit("const ");
    }
    emit("GomValue " + node->name);
    if (node->initializer) {
        emit(" = ");
        generateExpression(node->initializer.get());
    }
    emit(";\n");
}

void CodeGenerator::generateAssignment(const Assignment* node) {
    indent();
    emit(node->name + " = ");
    generateExpression(node->value.get());
    emit(";\n");
}

void CodeGenerator::generateFunctionDef(const FunctionDef* node) {
    indent();
    emit("auto " + node->name + " = [&](");
    
    // Parameters
    for (size_t i = 0; i < node->params.size(); i++) {
        emit("GomValue " + node->params[i]);
        if (i < node->params.size() - 1) emit(", ");
    }
    
    emit(") -> GomValue {\n");
    indentLevel++;
    
    // Body
    for (const auto& stmt : node->body) {
        generateStatement(stmt.get());
    }
    
    indentLevel--;
    indent();
    emit("};\n");
}

void CodeGenerator::generateClassDef(const ClassDef* node) {
    emitLine("// Class " + node->name + " - classes not fully implemented yet");
}

void CodeGenerator::generateIfStatement(const IfStatement* node) {
    indent();
    emit("if (gom_to_bool(");
    generateExpression(node->condition.get());
    emit(")) {\n");
    
    indentLevel++;
    for (const auto& stmt : node->thenBranch) {
        generateStatement(stmt.get());
    }
    indentLevel--;
    
    indent();
    emit("}\n");
}

void CodeGenerator::generateReturnStatement(const ReturnStatement* node) {
    indent();
    emit("return ");
    if (node->value) {
        generateExpression(node->value.get());
    } else {
        emit("GomValue()");
    }
    emit(";\n");
}

void CodeGenerator::generateBinaryOp(const BinaryOp* node) {
    emit("gom_binary_op(");
    generateExpression(node->left.get());
    emit(", \"" + node->op + "\", ");
    generateExpression(node->right.get());
    emit(")");
}

void CodeGenerator::generateUnaryOp(const UnaryOp* node) {
    emit("gom_unary_op(\"" + node->op + "\", ");
    generateExpression(node->operand.get());
    emit(")");
}

void CodeGenerator::generateFunctionCall(const FunctionCall* node) {
    if (node->name == "print") {
        emit("gom_print(");
        if (!node->args.empty()) {
            generateExpression(node->args[0].get());
        }
        emit(")");
    } else {
        emit(node->name + "(");
        for (size_t i = 0; i < node->args.size(); i++) {
            generateExpression(node->args[i].get());
            if (i < node->args.size() - 1) emit(", ");
        }
        emit(")");
    }
}

void CodeGenerator::generateArrayLiteral(const ArrayLiteral* node) {
    emit("GomValue(std::vector<GomValue>{");
    for (size_t i = 0; i < node->elements.size(); i++) {
        generateExpression(node->elements[i].get());
        if (i < node->elements.size() - 1) emit(", ");
    }
    emit("})");
}

void CodeGenerator::generateIndexAccess(const IndexAccess* node) {
    emit("gom_index_access(");
    generateExpression(node->object.get());
    emit(", ");
    generateExpression(node->index.get());
    emit(")");
}

std::string CodeGenerator::generateRuntimeIncludes() {
    return R"(#include <iostream>
#include <string>
#include <vector>
#include <variant>
#include <memory>
#include <cmath>
)";
}

std::string CodeGenerator::generateRuntimeCode() {
    return R"(// Gulf of Mexico Runtime Library

class GomValue {
public:
    std::variant<double, std::string, bool, std::vector<GomValue>> data;
    
    GomValue() : data(0.0) {}
    GomValue(double d) : data(d) {}
    GomValue(const std::string& s) : data(s) {}
    GomValue(bool b) : data(b) {}
    GomValue(const std::vector<GomValue>& v) : data(v) {}
    
    double as_number() const {
        if (std::holds_alternative<double>(data)) return std::get<double>(data);
        if (std::holds_alternative<bool>(data)) return std::get<bool>(data) ? 1.0 : 0.0;
        if (std::holds_alternative<std::string>(data)) return std::stod(std::get<std::string>(data));
        return 0.0;
    }
    
    std::string as_string() const {
        if (std::holds_alternative<std::string>(data)) return std::get<std::string>(data);
        if (std::holds_alternative<double>(data)) return std::to_string(std::get<double>(data));
        if (std::holds_alternative<bool>(data)) return std::get<bool>(data) ? "true" : "false";
        return "undefined";
    }
    
    bool as_bool() const {
        if (std::holds_alternative<bool>(data)) return std::get<bool>(data);
        if (std::holds_alternative<double>(data)) return std::get<double>(data) != 0.0;
        if (std::holds_alternative<std::string>(data)) return !std::get<std::string>(data).empty();
        return false;
    }
};

bool gom_to_bool(const GomValue& v) {
    return v.as_bool();
}

void gom_print(const GomValue& v) {
    std::cout << v.as_string() << std::endl;
}

GomValue gom_binary_op(const GomValue& left, const std::string& op, const GomValue& right) {
    if (op == "+") return GomValue(left.as_number() + right.as_number());
    if (op == "-") return GomValue(left.as_number() - right.as_number());
    if (op == "*") return GomValue(left.as_number() * right.as_number());
    if (op == "/") return GomValue(left.as_number() / right.as_number());
    if (op == "%") return GomValue(fmod(left.as_number(), right.as_number()));
    if (op == "==") return GomValue(left.as_number() == right.as_number());
    if (op == "!=") return GomValue(left.as_number() != right.as_number());
    if (op == "<") return GomValue(left.as_number() < right.as_number());
    if (op == ">") return GomValue(left.as_number() > right.as_number());
    if (op == "<=") return GomValue(left.as_number() <= right.as_number());
    if (op == ">=") return GomValue(left.as_number() >= right.as_number());
    if (op == "&&") return GomValue(left.as_bool() && right.as_bool());
    if (op == "||") return GomValue(left.as_bool() || right.as_bool());
    if (op == "~=") return GomValue(std::abs(left.as_number() - right.as_number()) < 0.01);
    return GomValue();
}

GomValue gom_unary_op(const std::string& op, const GomValue& operand) {
    if (op == "-") return GomValue(-operand.as_number());
    if (op == "!") return GomValue(!operand.as_bool());
    return GomValue();
}

GomValue gom_index_access(const GomValue& obj, const GomValue& index) {
    if (std::holds_alternative<std::vector<GomValue>>(obj.data)) {
        const auto& vec = std::get<std::vector<GomValue>>(obj.data);
        int idx = static_cast<int>(index.as_number());
        // Support negative indexing (-1 = last element)
        if (idx < 0) idx += vec.size();
        if (idx >= 0 && idx < vec.size()) {
            return vec[idx];
        }
    }
    return GomValue();
}
)";
}

} // namespace gom
