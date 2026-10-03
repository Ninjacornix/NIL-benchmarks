#include <algorithm>
#include <cctype>
#include <fstream>
#include <iterator>
#include <numeric>
#include <sstream>
#include <string>
#include <vector>

std::vector<long long> numbers(const std::string &text) {
    std::vector<long long> values;
    std::istringstream stream(text);
    std::string item;
    while (std::getline(stream, item, ','))
        values.push_back(std::stoll(item));
    return values;
}

std::string transform(const std::string &data) {
    auto p = data.find('\n');
    auto key = numbers(data.substr(0, p));
    if (std::gcd(key[0], 26LL) != 1)
        return "error\n";
    std::string clean;
    for (unsigned char x : data.substr(p + 1)) {
        x = std::tolower(x);
        if (x >= 'a' && x <= 'z')
            clean += char('a' + (key[0] * (x - 'a') + key[1]) % 26);
        else if (x >= '0' && x <= '9')
            clean += x;
    }
    std::string out;
    for (size_t i = 0; i < clean.size(); ++i) {
        if (i && i % 5 == 0)
            out += ' ';
        out += clean[i];
    }
    return out;
}

long long solve(const std::string &input_path, const std::string &output_path) {
    std::ifstream input_file(input_path, std::ios::binary);
    const std::string data((std::istreambuf_iterator<char>(input_file)),
                           std::istreambuf_iterator<char>());
    const std::string output = transform(data);
    std::ofstream output_file(output_path, std::ios::binary);
    output_file.write(output.data(), static_cast<std::streamsize>(output.size()));
    return static_cast<long long>(output.size());
}
