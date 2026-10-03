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
    auto rolls = numbers(data);
    for (auto n : rolls)
        if (n < 0 || n > 10)
            return "error\n";
    size_t p = 0;
    long long score = 0;
    for (int frame = 0; frame < 9; ++frame) {
        if (p + 1 >= rolls.size())
            return "error\n";
        if (rolls[p] == 10) {
            if (p + 2 >= rolls.size())
                return "error\n";
            score += rolls[p] + rolls[p + 1] + rolls[p + 2];
            ++p;
        } else {
            auto sum = rolls[p] + rolls[p + 1];
            if (sum > 10)
                return "error\n";
            score += sum;
            if (sum == 10) {
                if (p + 2 >= rolls.size())
                    return "error\n";
                score += rolls[p + 2];
            }
            p += 2;
        }
    }
    if (p + 1 >= rolls.size())
        return "error\n";
    auto first = rolls[p], second = rolls[p + 1];
    if (first < 10 && first + second > 10)
        return "error\n";
    bool bonus = first == 10 || first + second == 10;
    if (rolls.size() - p != (bonus ? 3 : 2))
        return "error\n";
    if (first == 10 && second < 10 && second + rolls[p + 2] > 10)
        return "error\n";
    for (; p < rolls.size(); ++p)
        score += rolls[p];
    return std::to_string(score) + "\n";
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
