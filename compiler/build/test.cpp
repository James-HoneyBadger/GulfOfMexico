#include <iostream>
#include <string>
#include <vector>
#include <variant>
#include <memory>
#include <cmath>

// Gulf of Mexico Runtime Library

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

int main() {
    gom_print(GomValue(std::string("Testing Satirical Features")));
    // Satirical: happy
    {
        gom_print(GomValue(std::string("Happy code block!")));
    }
    // Satirical: lucky
    {
        const GomValue x;
        GomValue(42.000000);
        gom_print(GomValue(std::string("Lucky number")));
        gom_print(x);
    }
    // Satirical: blockchain
    {
        gom_print(GomValue(std::string("Decentralized!")));
    }
    // Satirical: ai_powered
    {
        const GomValue prediction;
        GomValue(99.000000);
        gom_print(GomValue(std::string("AI Prediction")));
        gom_print(prediction);
    }
    // Satirical: sprint
    {
        gom_print(GomValue(std::string("Sprint velocity: Maximum!")));
    }
    // Satirical: synergize
    {
        const GomValue synergy;
        GomValue(100.000000);
        gom_print(GomValue(std::string("Synergy level")));
        gom_print(synergy);
    }
    gom_print(GomValue(std::string("All satirical features tested!")));
}
