#include <fstream>
#include <iterator>
#include <string>

long long solve(const std::string& input_path, const std::string& output_path) {
    std::ifstream input_file(input_path, std::ios::binary);
    const std::string data((std::istreambuf_iterator<char>(input_file)), std::istreambuf_iterator<char>());
    long long n = std::stoll(data), total = 0;
    std::string output;
    for (long long i = 0; i < n; ++i) {
        total += i;
        output += std::to_string(i) + ":" + std::to_string(total) + "\n";
    }
    std::ofstream output_file(output_path, std::ios::binary);
    output_file.write(output.data(), static_cast<std::streamsize>(output.size()));
    return static_cast<long long>(output.size());
}
