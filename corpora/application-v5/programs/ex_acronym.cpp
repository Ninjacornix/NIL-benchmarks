#include <cctype>
#include <fstream>
#include <iterator>
#include <string>

std::string transform(const std::string &data) {
    std::string output;
    bool start = true;
    for (unsigned char x : data) {
        if (x == '-' || std::isspace(x)) {
            start = true;
        } else if (std::isalpha(x)) {
            if (start)
                output += std::toupper(x);
            start = false;
        }
    }
    return output;
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
