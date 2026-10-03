#include <cmath>
#include <fstream>
#include <iterator>
#include <string>

std::string transform(const std::string &data) {
    int n = data[0] - 'A';
    std::string out;
    for (int row = 0; row <= 2 * n; ++row) {
        int offset = n - std::abs(row - n);
        std::string line(2 * n + 1, ' ');
        line[n - offset] = line[n + offset] = char('A' + offset);
        out += line + "\n";
    }
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
