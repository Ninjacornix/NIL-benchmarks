#include <algorithm>
#include <fstream>
#include <iterator>
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
    auto bases = numbers(data.substr(0, p));
    auto digits = numbers(data.substr(p + 1));
    if (bases[0] < 2 || bases[1] < 2)
        return "error\n";
    long long value = 0;
    for (auto d : digits) {
        if (d < 0 || d >= bases[0])
            return "error\n";
        value = value * bases[0] + d;
    }
    std::vector<long long> result;
    do {
        result.push_back(value % bases[1]);
        value /= bases[1];
    } while (value);
    std::string out;
    for (auto it = result.rbegin(); it != result.rend(); ++it)
        out += std::to_string(*it) + "\n";
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
