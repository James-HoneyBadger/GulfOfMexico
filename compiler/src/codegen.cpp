#include "codegen.h"
#include <iostream>
#include <unordered_set>

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
    } else if (auto* satStmt = dynamic_cast<const SatiricalStatement*>(node)) {
        generateSatiricalStatement(satStmt);
    } else if (auto* delStmt = dynamic_cast<const DeleteStatement*>(node)) {
        generateDeleteStatement(delStmt);
    } else if (auto* revStmt = dynamic_cast<const ReverseStatement*>(node)) {
        generateReverseStatement(revStmt);
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
        // Properly escape string literals for C++
        std::string escaped;
        for (char c : str->value) {
            if (c == '"') escaped += "\\\"";
            else if (c == '\\') escaped += "\\\\";
            else if (c == '\n') escaped += "\\n";
            else if (c == '\t') escaped += "\\t";
            else if (c == '\r') escaped += "\\r";
            else escaped += c;
        }
        emit("GomValue(std::string(\"" + escaped + "\"))");
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
    // Built-in functions that map to gom_* runtime functions
    static const std::unordered_set<std::string> builtins = {
        "Number", "String", "Boolean", "Map",
        "sin", "cos", "tan", "sqrt", "abs", "floor", "ceil", "round",
        "log", "log10", "exp", "pow",
        "mean", "median", "stdev", "variance", "min_val", "max_val", "sum_list",
        "compound_interest", "simple_interest", "pmt",
        "roi", "profit_margin", "cagr",
        "linear_regression", "quadratic_solve"
    };

    if (node->name == "print") {
        emit("gom_print(");
        if (!node->args.empty()) {
            generateExpression(node->args[0].get());
        }
        emit(")");
    } else if (builtins.count(node->name)) {
        // Map built-in function calls to gom_* runtime functions
        emit("gom_" + node->name + "(");
        for (size_t i = 0; i < node->args.size(); i++) {
            generateExpression(node->args[i].get());
            if (i < node->args.size() - 1) emit(", ");
        }
        emit(")");
    } else {
        // User-defined functions
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

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <algorithm>
#include <stdexcept>
#include <variant>
#include <sstream>
#include <functional>
#include <cmath>

class GomValue {
public:
    std::variant<double, std::string, bool, std::vector<GomValue>, std::map<std::string, GomValue>> data;

    GomValue() : data(0.0) {}
    GomValue(double d) : data(d) {}
    GomValue(const std::string& s) : data(s) {}
    GomValue(bool b) : data(b) {}
    GomValue(const std::vector<GomValue>& v) : data(v) {}
    GomValue(const std::map<std::string, GomValue>& m) : data(m) {}

    double as_number() const {
        if (std::holds_alternative<double>(data)) return std::get<double>(data);
        if (std::holds_alternative<bool>(data)) return std::get<bool>(data) ? 1.0 : 0.0;
        if (std::holds_alternative<std::string>(data)) {
            try {
                return std::stod(std::get<std::string>(data));
            } catch (...) {
                return 0.0;
            }
        }
        return 0.0;
    }

    std::string as_string() const {
        if (std::holds_alternative<std::string>(data)) return std::get<std::string>(data);
        if (std::holds_alternative<double>(data)) return std::to_string(std::get<double>(data));
        if (std::holds_alternative<bool>(data)) return std::get<bool>(data) ? "true" : "false";
        if (std::holds_alternative<std::vector<GomValue>>(data)) {
            const auto& vec = std::get<std::vector<GomValue>>(data);
            std::string result = "[";
            for (size_t i = 0; i < vec.size(); i++) {
                result += vec[i].as_string();
                if (i < vec.size() - 1) result += ", ";
            }
            result += "]";
            return result;
        }
        if (std::holds_alternative<std::map<std::string, GomValue>>(data)) {
            return "{map}";
        }
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
    if (std::holds_alternative<std::map<std::string, GomValue>>(obj.data)) {
        const auto& map = std::get<std::map<std::string, GomValue>>(obj.data);
        auto it = map.find(index.as_string());
        if (it != map.end()) {
            return it->second;
        }
    }
    return GomValue();
}

// Type conversion functions
GomValue gom_Number(const GomValue& v) {
    return GomValue(v.as_number());
}

GomValue gom_String(const GomValue& v) {
    return GomValue(v.as_string());
}

GomValue gom_Boolean(const GomValue& v) {
    return GomValue(v.as_bool());
}

GomValue gom_Map() {
    return GomValue(std::map<std::string, GomValue>());
}

// Math functions
GomValue gom_sin(const GomValue& v) { return GomValue(std::sin(v.as_number())); }
GomValue gom_cos(const GomValue& v) { return GomValue(std::cos(v.as_number())); }
GomValue gom_tan(const GomValue& v) { return GomValue(std::tan(v.as_number())); }
GomValue gom_sqrt(const GomValue& v) { return GomValue(std::sqrt(v.as_number())); }
GomValue gom_abs(const GomValue& v) { return GomValue(std::abs(v.as_number())); }
GomValue gom_floor(const GomValue& v) { return GomValue(std::floor(v.as_number())); }
GomValue gom_ceil(const GomValue& v) { return GomValue(std::ceil(v.as_number())); }
GomValue gom_round(const GomValue& v) { return GomValue(std::round(v.as_number())); }
GomValue gom_log(const GomValue& v) { return GomValue(std::log(v.as_number())); }
GomValue gom_log10(const GomValue& v) { return GomValue(std::log10(v.as_number())); }
GomValue gom_exp(const GomValue& v) { return GomValue(std::exp(v.as_number())); }
GomValue gom_pow(const GomValue& base, const GomValue& exp) {
    return GomValue(std::pow(base.as_number(), exp.as_number()));
}

// Statistical functions
GomValue gom_mean(const GomValue& list) {
    if (!std::holds_alternative<std::vector<GomValue>>(list.data)) return GomValue(0.0);
    const auto& vec = std::get<std::vector<GomValue>>(list.data);
    if (vec.empty()) return GomValue(0.0);
    double sum = 0.0;
    for (const auto& v : vec) sum += v.as_number();
    return GomValue(sum / vec.size());
}

GomValue gom_median(const GomValue& list) {
    if (!std::holds_alternative<std::vector<GomValue>>(list.data)) return GomValue(0.0);
    auto vec = std::get<std::vector<GomValue>>(list.data);
    if (vec.empty()) return GomValue(0.0);
    std::vector<double> nums;
    for (const auto& v : vec) nums.push_back(v.as_number());
    std::sort(nums.begin(), nums.end());
    size_t mid = nums.size() / 2;
    if (nums.size() % 2 == 0) {
        return GomValue((nums[mid-1] + nums[mid]) / 2.0);
    }
    return GomValue(nums[mid]);
}

GomValue gom_stdev(const GomValue& list) {
    if (!std::holds_alternative<std::vector<GomValue>>(list.data)) return GomValue(0.0);
    const auto& vec = std::get<std::vector<GomValue>>(list.data);
    if (vec.size() < 2) return GomValue(0.0);

    double mean = gom_mean(list).as_number();
    double sum_sq_diff = 0.0;
    for (const auto& v : vec) {
        double diff = v.as_number() - mean;
        sum_sq_diff += diff * diff;
    }
    return GomValue(std::sqrt(sum_sq_diff / (vec.size() - 1)));
}

GomValue gom_variance(const GomValue& list) {
    double sd = gom_stdev(list).as_number();
    return GomValue(sd * sd);
}

GomValue gom_min_val(const GomValue& list) {
    if (!std::holds_alternative<std::vector<GomValue>>(list.data)) return GomValue(0.0);
    const auto& vec = std::get<std::vector<GomValue>>(list.data);
    if (vec.empty()) return GomValue(0.0);
    double min = vec[0].as_number();
    for (const auto& v : vec) {
        double val = v.as_number();
        if (val < min) min = val;
    }
    return GomValue(min);
}

GomValue gom_max_val(const GomValue& list) {
    if (!std::holds_alternative<std::vector<GomValue>>(list.data)) return GomValue(0.0);
    const auto& vec = std::get<std::vector<GomValue>>(list.data);
    if (vec.empty()) return GomValue(0.0);
    double max = vec[0].as_number();
    for (const auto& v : vec) {
        double val = v.as_number();
        if (val > max) max = val;
    }
    return GomValue(max);
}

GomValue gom_sum_list(const GomValue& list) {
    if (!std::holds_alternative<std::vector<GomValue>>(list.data)) return GomValue(0.0);
    const auto& vec = std::get<std::vector<GomValue>>(list.data);
    double sum = 0.0;
    for (const auto& v : vec) sum += v.as_number();
    return GomValue(sum);
}

// Financial functions
GomValue gom_compound_interest(const GomValue& principal, const GomValue& rate,
                               const GomValue& time, const GomValue& n) {
    double p = principal.as_number();
    double r = rate.as_number();
    double t = time.as_number();
    double num = n.as_number();
    double amount = p * std::pow(1 + r/num, num * t);
    return GomValue(amount);
}

GomValue gom_simple_interest(const GomValue& principal, const GomValue& rate, const GomValue& time) {
    double p = principal.as_number();
    double r = rate.as_number();
    double t = time.as_number();
    return GomValue(p * (1 + r * t));
}

GomValue gom_pmt(const GomValue& rate, const GomValue& nper, const GomValue& pv) {
    double r = rate.as_number();
    double n = nper.as_number();
    double p = pv.as_number();
    if (r == 0) return GomValue(-p / n);
    double payment = p * (r * std::pow(1 + r, n)) / (std::pow(1 + r, n) - 1);
    return GomValue(payment);
}

// Business metrics
GomValue gom_roi(const GomValue& gain, const GomValue& cost) {
    double g = gain.as_number();
    double c = cost.as_number();
    if (c == 0) return GomValue(0.0);
    return GomValue((g - c) / c * 100.0);
}

GomValue gom_profit_margin(const GomValue& revenue, const GomValue& cost) {
    double r = revenue.as_number();
    double c = cost.as_number();
    if (r == 0) return GomValue(0.0);
    return GomValue((r - c) / r * 100.0);
}

GomValue gom_cagr(const GomValue& begin_val, const GomValue& end_val, const GomValue& years) {
    double bv = begin_val.as_number();
    double ev = end_val.as_number();
    double y = years.as_number();
    if (bv == 0 || y == 0) return GomValue(0.0);
    return GomValue((std::pow(ev / bv, 1.0 / y) - 1.0) * 100.0);
}

// Scientific functions
GomValue gom_linear_regression(const GomValue& x_list, const GomValue& y_list) {
    if (!std::holds_alternative<std::vector<GomValue>>(x_list.data) ||
        !std::holds_alternative<std::vector<GomValue>>(y_list.data)) {
        return GomValue(std::vector<GomValue>{GomValue(0.0), GomValue(0.0)});
    }

    const auto& x_vec = std::get<std::vector<GomValue>>(x_list.data);
    const auto& y_vec = std::get<std::vector<GomValue>>(y_list.data);

    if (x_vec.size() != y_vec.size() || x_vec.size() < 2) {
        return GomValue(std::vector<GomValue>{GomValue(0.0), GomValue(0.0)});
    }

    size_t n = x_vec.size();
    double x_mean = 0.0, y_mean = 0.0;
    for (size_t i = 0; i < n; i++) {
        x_mean += x_vec[i].as_number();
        y_mean += y_vec[i].as_number();
    }
    x_mean /= n;
    y_mean /= n;

    double numerator = 0.0, denominator = 0.0;
    for (size_t i = 0; i < n; i++) {
        double x_diff = x_vec[i].as_number() - x_mean;
        double y_diff = y_vec[i].as_number() - y_mean;
        numerator += x_diff * y_diff;
        denominator += x_diff * x_diff;
    }

    if (denominator == 0) {
        return GomValue(std::vector<GomValue>{GomValue(0.0), GomValue(0.0)});
    }

    double slope = numerator / denominator;
    double intercept = y_mean - slope * x_mean;

    return GomValue(std::vector<GomValue>{GomValue(slope), GomValue(intercept)});
}

GomValue gom_quadratic_solve(const GomValue& a, const GomValue& b, const GomValue& c) {
    double av = a.as_number();
    double bv = b.as_number();
    double cv = c.as_number();

    if (av == 0) return GomValue(std::vector<GomValue>{GomValue(0.0), GomValue(0.0)});

    double discriminant = bv * bv - 4 * av * cv;
    if (discriminant < 0) return GomValue(std::vector<GomValue>{GomValue(0.0), GomValue(0.0)});

    double root1 = (-bv + std::sqrt(discriminant)) / (2 * av);
    double root2 = (-bv - std::sqrt(discriminant)) / (2 * av);

    return GomValue(std::vector<GomValue>{GomValue(root1), GomValue(root2)});
}
)";
}

void CodeGenerator::generateSatiricalStatement(const SatiricalStatement* node) {
    emitLine("// Satirical: " + node->keyword);
    emitLine("{");
    indentLevel++;
    for (const auto& stmt : node->body) {
        generateStatement(stmt.get());
    }
    indentLevel--;
    emitLine("}");
}

void CodeGenerator::generateDeleteStatement(const DeleteStatement* node) {
    emitLine("// delete " + node->name + " (not implemented in compiled code)");
}

void CodeGenerator::generateReverseStatement(const ReverseStatement* node) {
    emitLine("// reverse " + node->name + " (not implemented in compiled code)");
}

} // namespace gom
