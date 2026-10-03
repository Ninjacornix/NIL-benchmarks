#include <fstream>
#include <iterator>
#include <set>
#include <sstream>
#include <string>

std::string transform(const std::string &data) {
    std::set<std::string> seen;
    std::istringstream in(data);
    std::string line;
    while (std::getline(in, line)) {
        if (!seen.insert(line.substr(5)).second)
            return "true\n";
    }
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
