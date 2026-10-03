#include <cctype>
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
    auto v = numbers(data);
    static const std::string names[] = {"no",  "one",   "two",   "three", "four", "five",
                                        "six", "seven", "eight", "nine",  "ten"};
    std::string out;
    for (int i = 0; i < v[1]; ++i) {
        int n = v[0] - i;
        if (i)
            out += "\n";
        auto word = names[n];
        word[0] = std::toupper(static_cast<unsigned char>(word[0]));
        auto line = word + " green " + (n == 1 ? "bottle" : "bottles") + " hanging on the wall,\n";
        out += line + line + "And if one green bottle should accidentally fall,\nThere'll be " +
               names[n - 1] + " green " + (n == 2 ? "bottle" : "bottles") +
               " hanging on the wall.\n";
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
