#include <algorithm>
#include <fstream>
#include <iterator>
#include <set>
#include <sstream>
#include <string>
#include <vector>

std::string transform(const std::string &data) {
    std::istringstream in(data);
    std::string row;
    std::vector<std::pair<int, std::string>> students;
    std::set<std::string> seen;
    while (std::getline(in, row)) {
        auto p = row.find('	');
        auto name = row.substr(p + 1);
        if (seen.insert(name).second)
            students.push_back({std::stoi(row.substr(0, p)), name});
    }
    std::sort(students.begin(), students.end());
    std::string out;
    for (auto [grade, name] : students)
        out += name + "\n";
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
