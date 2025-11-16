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
    const GomValue message = GomValue(std::string("Welcome to GulfOfMexico!"));
    const GomValue version = GomValue(2.000000);
    const GomValue isAwesome = GomValue(true);
    gom_print(message);
    gom_print(GomValue(std::string("Version:")));
    gom_print(version);
    const GomValue a = GomValue(10.000000);
    const GomValue b = GomValue(20.000000);
    const GomValue sum = gom_binary_op(a, "+", b);
    const GomValue product = gom_binary_op(a, "*", b);
    const GomValue difference = gom_binary_op(b, "-", a);
    const GomValue quotient = gom_binary_op(b, "/", a);
    gom_print(GomValue(std::string("Arithmetic:")));
    gom_print(sum);
    gom_print(product);
    gom_print(difference);
    gom_print(quotient);
    const GomValue numbers = GomValue(std::vector<GomValue>{GomValue(100.000000), GomValue(200.000000), GomValue(300.000000), GomValue(400.000000), GomValue(500.000000)});
    gom_print(GomValue(std::string("Array operations:")));
    gom_print(gom_index_access(numbers, GomValue(0.000000)));
    gom_print(gom_index_access(numbers, GomValue(2.000000)));
    gom_print(gom_index_access(numbers, gom_unary_op("-", GomValue(1.000000))));
    auto add = [&](GomValue x, GomValue y) -> GomValue {
        return gom_binary_op(x, "+", y);
    };
    auto multiply = [&](GomValue x, GomValue y) -> GomValue {
        return gom_binary_op(x, "*", y);
    };
    auto square = [&](GomValue n) -> GomValue {
        return gom_binary_op(n, "*", n);
    };
    gom_print(GomValue(std::string("Functions:")));
    gom_print(add(GomValue(15.000000), GomValue(25.000000)));
    gom_print(multiply(GomValue(7.000000), GomValue(8.000000)));
    gom_print(square(GomValue(9.000000)));
    const GomValue result = add(multiply(GomValue(3.000000), GomValue(4.000000)), square(GomValue(5.000000)));
    gom_print(GomValue(std::string("Nested calls:")));
    gom_print(result);
    const GomValue x = GomValue(50.000000);
    const GomValue y = GomValue(30.000000);
    if (gom_to_bool(gom_binary_op(x, ">", y))) {
        gom_print(GomValue(std::string("x is greater")));
    }
    if (gom_to_bool(gom_binary_op(y, "<", x))) {
        gom_print(GomValue(std::string("y is less")));
    }
    const GomValue max = GomValue(100.000000);
    const GomValue min = GomValue(10.000000);
    if (gom_to_bool(gom_binary_op(max, ">", min))) {
        const GomValue range = gom_binary_op(max, "-", min);
        gom_print(GomValue(std::string("Range:")));
        gom_print(range);
    }
    const GomValue fibonacci = GomValue(std::vector<GomValue>{GomValue(1.000000), GomValue(1.000000), GomValue(2.000000), GomValue(3.000000), GomValue(5.000000), GomValue(8.000000), GomValue(13.000000), GomValue(21.000000), GomValue(34.000000)});
    const GomValue fib_sum = gom_binary_op(gom_binary_op(gom_index_access(fibonacci, GomValue(0.000000)), "+", gom_index_access(fibonacci, GomValue(4.000000))), "+", gom_index_access(fibonacci, GomValue(8.000000)));
    gom_print(GomValue(std::string("Fibonacci sum:")));
    gom_print(fib_sum);
    const GomValue data = GomValue(std::vector<GomValue>{GomValue(10.000000), GomValue(20.000000), GomValue(30.000000), GomValue(40.000000), GomValue(50.000000)});
    const GomValue first = gom_index_access(data, GomValue(0.000000));
    const GomValue last = gom_index_access(data, gom_unary_op("-", GomValue(1.000000)));
    const GomValue middle = gom_index_access(data, GomValue(2.000000));
    gom_print(GomValue(std::string("Array elements:")));
    gom_print(first);
    gom_print(middle);
    gom_print(last);
    const GomValue isPositive = GomValue(true);
    const GomValue isNegative = GomValue(false);
    if (gom_to_bool(isPositive)) {
        gom_print(GomValue(std::string("Positive!")));
    }
    const GomValue calculation = gom_binary_op(gom_binary_op(gom_binary_op(gom_binary_op(GomValue(10.000000), "+", GomValue(5.000000)), "*", GomValue(3.000000)), "-", GomValue(20.000000)), "/", GomValue(5.000000));
    gom_print(GomValue(std::string("Complex calculation:")));
    gom_print(calculation);
    auto twice = [&](GomValue n) -> GomValue {
        return gom_binary_op(n, "*", GomValue(2.000000));
    };
    auto addTen = [&](GomValue n) -> GomValue {
        return gom_binary_op(n, "+", GomValue(10.000000));
    };
    const GomValue composed = addTen(twice(GomValue(20.000000)));
    gom_print(GomValue(std::string("Function composition:")));
    gom_print(composed);
    const GomValue price = GomValue(99.990000);
    const GomValue quantity = GomValue(3.000000);
    const GomValue tax = GomValue(0.080000);
    const GomValue total = gom_binary_op(gom_binary_op(price, "*", quantity), "*", gom_binary_op(GomValue(1.000000), "+", tax));
    gom_print(GomValue(std::string("Shopping cart:")));
    gom_print(total);
    gom_print(GomValue(std::string("Showcase complete!")));
}
