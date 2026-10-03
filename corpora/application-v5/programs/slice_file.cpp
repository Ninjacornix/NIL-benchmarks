#include <fstream>
#include <iterator>
#include <string>

long long solve(const std::string& input_path, const std::string& output_path) {
    std::ifstream input_file(input_path, std::ios::binary);
    const std::string data((std::istreambuf_iterator<char>(input_file)), std::istreambuf_iterator<char>());
    auto newline = data.find('\n'), comma = data.find(',');
    auto start = std::stoull(data.substr(0, comma));
    auto length = std::stoull(data.substr(comma + 1, newline - comma - 1));
    std::string output = data.substr(newline + 1 + start, length);
    std::ofstream output_file(output_path, std::ios::binary);
    output_file.write(output.data(), static_cast<std::streamsize>(output.size()));
    return static_cast<long long>(output.size());
}
