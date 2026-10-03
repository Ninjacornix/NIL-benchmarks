#include <algorithm>
#include <fstream>
#include <functional>
#include <iterator>
#include <map>
#include <numeric>
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
    auto basket = numbers(data);
    std::vector<int> counts(5);
    for (auto n : basket)
        ++counts[n - 1];
    const int prices[] = {0, 800, 1520, 2160, 2560, 3000};
    std::map<std::vector<int>, int> memo;
    std::function<int(std::vector<int>)> cost = [&](std::vector<int> state) {
        if (memo.count(state))
            return memo[state];
        int best = std::accumulate(state.begin(), state.end(), 0) * 800;
        for (int mask = 1; mask < 32; ++mask) {
            auto next = state;
            int size = 0;
            bool valid = true;
            for (int i = 0; i < 5; ++i)
                if (mask & (1 << i)) {
                    ++size;
                    if (next[i] == 0)
                        valid = false;
                    --next[i];
                }
            if (valid)
                best = std::min(best, prices[size] + cost(next));
        }
        return memo[state] = best;
    };
    return std::to_string(cost(counts)) + "\n";
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
