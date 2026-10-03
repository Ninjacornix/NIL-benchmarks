#include <fstream>
#include <iterator>
#include <string>
#include <sstream>

long long solve(const std::string& input_path, const std::string& output_path) {
    std::ifstream input_file(input_path, std::ios::binary);
    const std::string data((std::istreambuf_iterator<char>(input_file)), std::istreambuf_iterator<char>());
    std::string output, row, previous;
    bool first = true;
    std::istringstream input(data);
    while (std::getline(input, row)) {
        if (first || row != previous) output += row + "\n";
        previous = row;
        first = false;
    }
    std::ofstream output_file(output_path, std::ios::binary);
    output_file.write(output.data(), static_cast<std::streamsize>(output.size()));
    return static_cast<long long>(output.size());
}
