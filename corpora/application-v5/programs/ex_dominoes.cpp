#include <fstream>
#include <iterator>
#include <map>
#include <set>
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
    std::istringstream stream(data);
    std::string line;
    std::map<long long, int> degree;
    std::vector<std::pair<long long, long long>> edges;
    while (std::getline(stream, line)) {
        auto pair = numbers(line);
        edges.push_back({pair[0], pair[1]});
        ++degree[pair[0]];
        ++degree[pair[1]];
    }
    if (edges.empty())
        return "true\n";
    std::set<long long> seen{edges[0].first};
    bool changed = true;
    while (changed) {
        auto old = seen.size();
        for (auto [a, b] : edges)
            if (seen.count(a) || seen.count(b)) {
                seen.insert(a);
                seen.insert(b);
            }
        changed = old != seen.size();
    }
    for (auto [vertex, count] : degree)
        if (count % 2)
            return "false\n";
    return seen.size() == degree.size() ? "true\n" : "false\n";
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
