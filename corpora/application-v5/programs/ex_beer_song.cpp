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
    auto values = numbers(data);
    auto bottles = [](long long n, bool capital) {
        std::string s = n == 0   ? "no more bottles"
                        : n == 1 ? "1 bottle"
                                 : std::to_string(n) + " bottles";
        if (capital && n == 0)
            s[0] = 'N';
        return s;
    };
    std::string out;
    for (int i = 0; i < values[1]; ++i) {
        auto n = values[0] - i;
        if (i)
            out += "\n";
        out += bottles(n, true) + " of beer on the wall, " + bottles(n, false) + " of beer.\n";
        out += n == 0
                   ? "Go to the store and buy some more, 99 bottles of beer on the wall.\n"
                   : "Take " + std::string(n == 1 ? "it" : "one") + " down and pass it around, " +
                         bottles(n - 1, false) + " of beer on the wall.\n";
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
