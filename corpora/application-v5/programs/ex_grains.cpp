#include <fstream>
#include <iterator>
#include <string>
#include <cstdint>

std::string transform(const std::string &data) {
    int square = std::stoi(data.substr(data.find(':') + 1));
    if (square < 1 || square > 64) return "error\n";
    return std::to_string(std::uint64_t{1} << (square - 1)) + "\n";
}

long long solve(const std::string &input_path, const std::string &output_path) {
    std::ifstream input_file(input_path, std::ios::binary);
    const std::string data((std::istreambuf_iterator<char>(input_file)), std::istreambuf_iterator<char>());
    auto output = transform(data);
    std::ofstream output_file(output_path, std::ios::binary);
    output_file.write(output.data(), static_cast<std::streamsize>(output.size()));
    return static_cast<long long>(output.size());
}
