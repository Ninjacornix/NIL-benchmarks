#include <fstream>
#include <iterator>
#include <string>
#include <sstream>
#include <algorithm>

long long solve(const std::string& input_path, const std::string& output_path) {
    std::ifstream input_file(input_path, std::ios::binary);
    const std::string data((std::istreambuf_iterator<char>(input_file)), std::istreambuf_iterator<char>());
    std::istringstream input(data);
    long long value;
    input >> value;
    long long lo = value, hi = value;
    while (input >> value) { lo = std::min(lo, value); hi = std::max(hi, value); }
    std::string output = std::to_string(lo) + "," + std::to_string(hi) + "\n";
    std::ofstream output_file(output_path, std::ios::binary);
    output_file.write(output.data(), static_cast<std::streamsize>(output.size()));
    return static_cast<long long>(output.size());
}
