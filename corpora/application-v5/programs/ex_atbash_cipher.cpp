#include <cctype>
#include <fstream>
#include <iterator>
#include <string>

std::string transform(const std::string &data) {
    std::string clean;
    for (unsigned char x : data) {
        x = std::tolower(x);
        if (x >= 'a' && x <= 'z')
            clean += char('z' - (x - 'a'));
        else if (x >= '0' && x <= '9')
            clean += x;
    }
    std::string result;
    for (size_t i = 0; i < clean.size(); ++i) {
        if (i && i % 5 == 0)
            result += ' ';
        result += clean[i];
    }
    return result;
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
