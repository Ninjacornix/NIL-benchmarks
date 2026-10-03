#include <fstream>
#include <iterator>
#include <string>
#include <vector>

long long solve(const std::string& input_path, const std::string& output_path) {
    std::ifstream input_file(input_path, std::ios::binary);
    const std::string data((std::istreambuf_iterator<char>(input_file)), std::istreambuf_iterator<char>());
    std::vector<long long> counts(10);
    for (unsigned char x : data) if (x >= '0' && x <= '9') ++counts[x - '0'];
    std::string output;
    for (int i = 0; i < 10; ++i) output += std::to_string(i) + ":" + std::to_string(counts[i]) + "\n";
    std::ofstream output_file(output_path, std::ios::binary);
    output_file.write(output.data(), static_cast<std::streamsize>(output.size()));
    return static_cast<long long>(output.size());
}
