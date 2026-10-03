#include <fstream>
#include <iterator>
#include <sstream>
#include <string>
#include <vector>

std::string transform(const std::string &data) {
    std::vector<std::string> rows;
    std::istringstream in(data);
    std::string line;
    while (std::getline(in, line))
        rows.push_back(line);
    if (rows.empty())
        return "";
    auto result = rows;
    int height = rows.size(), width = rows[0].size();
    for (int y = 0; y < height; ++y)
        for (int x = 0; x < width; ++x) {
            int count = 0;
            for (int dy = -1; dy <= 1; ++dy)
                for (int dx = -1; dx <= 1; ++dx) {
                    int yy = y + dy, xx = x + dx;
                    if ((dx || dy) && yy >= 0 && yy < height && xx >= 0 && xx < width)
                        count += rows[yy][xx] == '*';
                }
            if (rows[y][x] != '*' && count)
                result[y][x] = char('0' + count);
        }
    std::string out;
    for (auto row : result)
        out += row + "\n";
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
