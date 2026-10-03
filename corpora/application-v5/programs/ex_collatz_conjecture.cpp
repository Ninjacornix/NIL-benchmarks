#include <fstream>
#include <iterator>
#include <string>

std::string transform(const std::string &data) {
    auto n = std::stoll(data);
    if (n <= 0)
        return "error\n";
    int steps = 0;
    while (n != 1) {
        n = n % 2 ? 3 * n + 1 : n / 2;
        ++steps;
    }
    return std::to_string(steps) + "\n";
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
