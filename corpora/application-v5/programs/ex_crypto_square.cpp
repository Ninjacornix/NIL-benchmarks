#include <cctype>
#include <fstream>
#include <iterator>
#include <string>

std::string transform(const std::string &data) {
    std::string clean;
    for (unsigned char x : data) {
        x = std::tolower(x);
        if (std::isalnum(x))
            clean += x;
    }
    if (clean.empty())
        return "";
    size_t cols = 1;
    while (cols * cols < clean.size())
        ++cols;
    size_t rows = (clean.size() + cols - 1) / cols;
    clean.resize(rows * cols, ' ');
    std::string out;
    for (size_t col = 0; col < cols; ++col) {
        if (col)
            out += ' ';
        for (size_t row = 0; row < rows; ++row)
            out += clean[row * cols + col];
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
