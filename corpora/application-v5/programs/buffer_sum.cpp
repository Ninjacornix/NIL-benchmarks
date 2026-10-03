#include <fstream>
#include <iterator>
#include <string>
#include <sstream>
#include <vector>
#include <numeric>

long long reduce_buffer(const std::vector<long long>& values) {
    return std::accumulate(values.begin(), values.end(), 0LL);
}

long long solve(const std::string& input_path, const std::string& output_path) {
    std::ifstream input_file(input_path, std::ios::binary);
    const std::string data((std::istreambuf_iterator<char>(input_file)), std::istreambuf_iterator<char>());
    std::vector<long long> values;
    std::istringstream input(data);
    long long value;
    while (input >> value) values.push_back(value);
    std::string output = std::to_string(reduce_buffer(values)) + "\n";
    std::ofstream output_file(output_path, std::ios::binary);
    output_file.write(output.data(), static_cast<std::streamsize>(output.size()));
    return static_cast<long long>(output.size());
}
