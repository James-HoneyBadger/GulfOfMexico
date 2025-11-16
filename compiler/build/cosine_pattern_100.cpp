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
    gom_print(GomValue(std::string("                    @")));
    gom_print(GomValue(std::string("                  #")));
    gom_print(GomValue(std::string("             *")));
    gom_print(GomValue(std::string("      &")));
    gom_print(GomValue(std::string("   %")));
    gom_print(GomValue(std::string("?")));
    gom_print(GomValue(std::string("   X")));
    gom_print(GomValue(std::string("      =")));
    gom_print(GomValue(std::string("             +")));
    gom_print(GomValue(std::string("                  ~")));
    gom_print(GomValue(std::string("                    $")));
    gom_print(GomValue(std::string("                  7")));
    gom_print(GomValue(std::string("             a")));
    gom_print(GomValue(std::string("      ^")));
    gom_print(GomValue(std::string("   ")));
    gom_print(GomValue(std::string("!")));
    gom_print(GomValue(std::string("   Z")));
    gom_print(GomValue(std::string("      :")));
    gom_print(GomValue(std::string("             [")));
    gom_print(GomValue(std::string("                  )")));
    gom_print(GomValue(std::string("                    R")));
    gom_print(GomValue(std::string("                  9")));
    gom_print(GomValue(std::string("             q")));
    gom_print(GomValue(std::string("      <")));
    gom_print(GomValue(std::string("   ;")));
    gom_print(GomValue(std::string("~")));
    gom_print(GomValue(std::string("   M")));
    gom_print(GomValue(std::string("      }")));
    gom_print(GomValue(std::string("             0")));
    gom_print(GomValue(std::string("                  B")));
    gom_print(GomValue(std::string("                    +")));
    gom_print(GomValue(std::string("                  @")));
    gom_print(GomValue(std::string("             ?")));
    gom_print(GomValue(std::string("      ")));
    gom_print(GomValue(std::string("   -")));
    gom_print(GomValue(std::string("^")));
    gom_print(GomValue(std::string("   8")));
    gom_print(GomValue(std::string("      ")));
    gom_print(GomValue(std::string("             Y")));
    gom_print(GomValue(std::string("                  k")));
    gom_print(GomValue(std::string("                    )")));
    gom_print(GomValue(std::string("                  D")));
    gom_print(GomValue(std::string("             5")));
    gom_print(GomValue(std::string("      s")));
    gom_print(GomValue(std::string("   ")));
    gom_print(GomValue(std::string(",")));
    gom_print(GomValue(std::string("   T")));
    gom_print(GomValue(std::string("      ")));
    gom_print(GomValue(std::string("             >")));
    gom_print(GomValue(std::string("                  n")));
    gom_print(GomValue(std::string("                    *")));
    gom_print(GomValue(std::string("                  F")));
    gom_print(GomValue(std::string("             3")));
    gom_print(GomValue(std::string("      u")));
    gom_print(GomValue(std::string("   ")));
    gom_print(GomValue(std::string(".")));
    gom_print(GomValue(std::string("   H")));
    gom_print(GomValue(std::string("      ")));
    gom_print(GomValue(std::string("             }")));
    gom_print(GomValue(std::string("                  v")));
    gom_print(GomValue(std::string("                    %")));
    gom_print(GomValue(std::string("                  L")));
    gom_print(GomValue(std::string("             2")));
    gom_print(GomValue(std::string("      t")));
    gom_print(GomValue(std::string("   ")));
    gom_print(GomValue(std::string("/")));
    gom_print(GomValue(std::string("   C")));
    gom_print(GomValue(std::string("      ")));
    gom_print(GomValue(std::string("             {")));
    gom_print(GomValue(std::string("                  r")));
    gom_print(GomValue(std::string("                    &")));
    gom_print(GomValue(std::string("                  J")));
    gom_print(GomValue(std::string("             6")));
    gom_print(GomValue(std::string("      w")));
    gom_print(GomValue(std::string("   ")));
    gom_print(GomValue(std::string("|")));
    gom_print(GomValue(std::string("   N")));
    gom_print(GomValue(std::string("      ")));
    gom_print(GomValue(std::string("             )")));
    gom_print(GomValue(std::string("                  e")));
    gom_print(GomValue(std::string("                    ^")));
    gom_print(GomValue(std::string("                  4")));
    gom_print(GomValue(std::string("             b")));
    gom_print(GomValue(std::string("      :")));
    gom_print(GomValue(std::string("   ")));
    gom_print(GomValue(std::string("=")));
    gom_print(GomValue(std::string("   Q")));
    gom_print(GomValue(std::string("      ")));
    gom_print(GomValue(std::string("             !")));
    gom_print(GomValue(std::string("                  x")));
    gom_print(GomValue(std::string("                    $")));
    gom_print(GomValue(std::string("                  1")));
    gom_print(GomValue(std::string("             j")));
    gom_print(GomValue(std::string("      >")));
    gom_print(GomValue(std::string("   ")));
    gom_print(GomValue(std::string("+")));
    gom_print(GomValue(std::string("   U")));
    gom_print(GomValue(std::string("      ")));
    gom_print(GomValue(std::string("             ~")));
    gom_print(GomValue(std::string("                  o")));
}
