#include <iostream>
#include <string>
#include <vector>
#include <variant>
#include <memory>
#include <cmath>

// Gulf of Mexico Runtime Library

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

int main() {
    const GomValue x = GomValue(10.000000);
    const GomValue y = GomValue(20.000000);
    const GomValue sum = gom_binary_op(x, "+", y);
    gom_print(sum);
}
