#include <fstream>
#include <iterator>
#include <string>
#include <cstdint>

std::string transform(const std::string &data) {
    __uint128_t number = 0, sum = 0;
    bool overflow = false;
    for (char digit : data) number = number * 10 + (digit - '0');
    for (char digit : data) {
        __uint128_t power = 1;
        for (std::size_t i = 0; i < data.size(); ++i) power *= digit - '0';
        auto next = sum + power;
        overflow = overflow || next < sum;
        sum = next;
    }
    return !overflow && sum == number ? "true\n" : "false\n";
}

long long solve(const std::string &input_path, const std::string &output_path) {
    std::ifstream input_file(input_path, std::ios::binary);
    const std::string data((std::istreambuf_iterator<char>(input_file)), std::istreambuf_iterator<char>());
    auto output = transform(data);
    std::ofstream output_file(output_path, std::ios::binary);
    output_file.write(output.data(), static_cast<std::streamsize>(output.size()));
    return static_cast<long long>(output.size());
}
