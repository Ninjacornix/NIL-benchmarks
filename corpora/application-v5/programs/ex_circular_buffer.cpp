#include <fstream>
#include <iterator>
#include <sstream>
#include <string>
#include <vector>

std::vector<long long> numbers(const std::string &text) {
    std::vector<long long> values;
    std::istringstream stream(text);
    std::string item;
    while (std::getline(stream, item, ','))
        values.push_back(std::stoll(item));
    return values;
}

std::string transform(const std::string &data) {
    std::istringstream in(data);
    std::string line;
    std::getline(in, line);
    size_t capacity = std::stoull(line);
    std::vector<long long> items;
    std::string out;
    while (std::getline(in, line)) {
        auto op = numbers(line);
        if (op[0] == 0) {
            if (items.empty())
                out += "error\n";
            else {
                out += std::to_string(items.front()) + "\n";
                items.erase(items.begin());
            }
        } else if (op[0] == 3) {
            items.clear();
            out += "ok\n";
        } else if (items.size() == capacity && op[0] == 1)
            out += "error\n";
        else {
            if (items.size() == capacity)
                items.erase(items.begin());
            items.push_back(op[1]);
            out += "ok\n";
        }
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
