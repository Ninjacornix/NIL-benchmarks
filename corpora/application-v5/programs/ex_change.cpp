#include <algorithm>
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
    auto p = data.find('\n');
    int target = std::stoi(data.substr(0, p));
    auto coins = numbers(data.substr(p + 1));
    if (target < 0)
        return "error\n";
    std::vector<int> best(target + 1, target + 1), last(target + 1);
    best[0] = 0;
    for (int value = 1; value <= target; ++value)
        for (auto coin : coins)
            if (coin <= value && best[value - coin] + 1 < best[value]) {
                best[value] = best[value - coin] + 1;
                last[value] = coin;
            }
    if (best[target] > target)
        return "error\n";
    std::vector<int> result;
    while (target) {
        result.push_back(last[target]);
        target -= last[target];
    }
    std::sort(result.begin(), result.end());
    std::string out;
    for (auto coin : result)
        out += std::to_string(coin) + "\n";
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
