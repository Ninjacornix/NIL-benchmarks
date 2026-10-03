#include <fstream>
#include <iterator>
#include <map>
#include <sstream>
#include <string>

long long solve(const std::string &input_path, const std::string &output_path) {
    std::ifstream input(input_path, std::ios::binary);
    const std::string data((std::istreambuf_iterator<char>(input)), {});
    // The frozen property uses a JSON object of decimal score keys and arrays
    // of single uppercase Latin letters. Scan complete quoted tokens, not fixtures.
    std::map<char, int> scores;
    auto position = data.find('"', data.find('{', data.find(':')));
    int score = 0;
    while (position != std::string::npos) {
        const auto end = data.find('"', position + 1);
        const auto token = data.substr(position + 1, end - position - 1);
        if (data[end + 1] == ':')
            score = std::stoi(token);
        else
            scores[static_cast<char>(token[0] - 'A' + 'a')] = score;
        position = data.find('"', end + 1);
    }
    std::string result = "{";
    for (auto [letter, value] : scores) {
        if (result.size() != 1) result += ',';
        result += '"'; result += letter; result += "\":";
        result += std::to_string(value);
    }
    result += '}';
    std::ofstream output(output_path, std::ios::binary);
    output.write(result.data(), static_cast<std::streamsize>(result.size()));
    return static_cast<long long>(result.size());
}
