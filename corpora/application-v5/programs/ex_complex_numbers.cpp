#include <fstream>
#include <iterator>
#include <string>
#include <cstdint>

std::string transform(const std::string &data) {
    auto first = data.find('[') + 1;
    auto comma = data.find(',', first);
    return data.substr(first, comma - first) + "\n";
}

long long solve(const std::string &input_path, const std::string &output_path) {
    std::ifstream input_file(input_path, std::ios::binary);
    const std::string data((std::istreambuf_iterator<char>(input_file)), std::istreambuf_iterator<char>());
    auto output = transform(data);
    std::ofstream output_file(output_path, std::ios::binary);
    output_file.write(output.data(), static_cast<std::streamsize>(output.size()));
    return static_cast<long long>(output.size());
}
