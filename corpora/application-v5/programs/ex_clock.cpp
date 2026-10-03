#include <algorithm>
#include <fstream>
#include <iomanip>
#include <iterator>
#include <sstream>
#include <string>

std::string transform(const std::string &data) {
    auto split = data.find(',');
    auto t = (std::stoll(data.substr(0, split)) * 60 + std::stoll(data.substr(split + 1))) % 1440;
    if (t < 0)
        t += 1440;
    std::ostringstream out;
    out << std::setfill('0') << std::setw(2) << t / 60 << ":" << std::setw(2) << t % 60;
    return out.str();
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
