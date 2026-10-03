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
    auto range = numbers(data);
    const std::string animals[] = {"",    "fly",  "spider", "bird", "cat",
                                   "dog", "goat", "cow",    "horse"};
    const std::string remarks[] = {"",
                                   "",
                                   "It wriggled and jiggled and tickled inside her.",
                                   "How absurd to swallow a bird!",
                                   "Imagine that, to swallow a cat!",
                                   "What a hog, to swallow a dog!",
                                   "Just opened her throat and swallowed a goat!",
                                   "I don't know how she swallowed a cow!",
                                   "She's dead, of course!"};
    std::string out;
    for (int n = range[0]; n <= range[1]; ++n) {
        if (n != range[0])
            out += "\n";
        out += "I know an old lady who swallowed a " + animals[n] + ".\n";
        if (n > 1)
            out += remarks[n] + "\n";
        if (n != 8) {
            for (int i = n; i > 1; --i)
                out += "She swallowed the " + animals[i] + " to catch the " + animals[i - 1] +
                       (i == 3 ? " that wriggled and jiggled and tickled inside her" : "") + ".\n";
            out += "I don't know why she swallowed the fly. Perhaps she'll die.\n";
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
