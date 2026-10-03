#include <algorithm>
#include <fstream>
#include <iterator>
#include <string>

std::string transform(const std::string &data) {
    static const std::string names[] = {"eggs",     "peanuts",   "shellfish", "strawberries",
                                        "tomatoes", "chocolate", "pollen",    "cats"};
    auto p = data.find('\n');
    auto score = std::stoll(data.substr(0, p));
    for (int i = 0; i < 8; ++i)
        if (data.substr(p + 1) == names[i])
            return score & (1LL << i) ? "true\n" : "false\n";
    return "false\n";
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
