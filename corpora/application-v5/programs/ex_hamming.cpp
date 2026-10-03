#include <algorithm>
#include <fstream>
#include <iterator>
#include <string>

std::string transform(const std::string &data) {
    auto split = data.find('\n');
    auto left = data.substr(0, split), right = data.substr(split + 1);
    if (left.size() != right.size())
        return "error\n";
    int distance = 0;
    for (size_t i = 0; i < left.size(); ++i)
        distance += left[i] != right[i];
    return std::to_string(distance) + "\n";
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
