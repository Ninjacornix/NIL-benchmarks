#include <fstream>
#include <iterator>
#include <string>
#include <sstream>
#include <vector>

long long dot(const std::vector<long long>& left, const std::vector<long long>& right) {
    long long total = 0;
    for (std::size_t i = 0; i < left.size(); ++i) total += left[i] * right[i];
    return total;
}

long long solve(const std::string& input_path, const std::string& output_path) {
    std::ifstream input_file(input_path, std::ios::binary);
    const std::string data((std::istreambuf_iterator<char>(input_file)), std::istreambuf_iterator<char>());
    std::vector<long long> left, right;
    std::string row;
    std::istringstream input(data);
    while (std::getline(input, row)) {
        auto comma = row.find(',');
        left.push_back(std::stoll(row.substr(0, comma)));
        right.push_back(std::stoll(row.substr(comma + 1)));
    }
    std::string output = std::to_string(dot(left, right)) + "\n";
    std::ofstream output_file(output_path, std::ios::binary);
    output_file.write(output.data(), static_cast<std::streamsize>(output.size()));
    return static_cast<long long>(output.size());
}
