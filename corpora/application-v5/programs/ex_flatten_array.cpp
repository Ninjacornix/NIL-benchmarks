#include <cctype>
#include <fstream>
#include <iterator>
#include <string>

std::string transform(const std::string &data) {
    std::string out;
    for (size_t i = 0; i < data.size();) {
        if (data[i] == '-' || std::isdigit(static_cast<unsigned char>(data[i]))) {
            size_t end = i + 1;
            while (end < data.size() && std::isdigit(static_cast<unsigned char>(data[end])))
                ++end;
            out += data.substr(i, end - i) + "\n";
            i = end;
        } else
            ++i;
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
