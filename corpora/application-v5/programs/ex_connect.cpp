#include <algorithm>
#include <fstream>
#include <iterator>
#include <queue>
#include <set>
#include <sstream>
#include <string>
#include <vector>

std::string transform(const std::string &data) {
    std::vector<std::string> rows;
    std::istringstream in(data);
    std::string row;
    while (std::getline(in, row)) {
        row.erase(std::remove(row.begin(), row.end(), ' '), row.end());
        rows.push_back(row);
    }
    if (rows.empty())
        return "";
    int h = rows.size(), w = rows[0].size();
    for (char symbol : {'X', 'O'}) {
        std::queue<std::pair<int, int>> todo;
        std::set<std::pair<int, int>> seen;
        for (int y = 0; y < h; ++y)
            for (int x = 0; x < w; ++x)
                if ((symbol == 'X' ? x == 0 : y == 0) && rows[y][x] == symbol) {
                    todo.push({y, x});
                    seen.insert({y, x});
                }
        while (!todo.empty()) {
            auto [y, x] = todo.front();
            todo.pop();
            if (symbol == 'X' ? x == w - 1 : y == h - 1)
                return std::string(1, symbol);
            for (auto [dy, dx] : std::vector<std::pair<int, int>>{
                     {-1, 0}, {-1, 1}, {0, -1}, {0, 1}, {1, -1}, {1, 0}}) {
                int yy = y + dy, xx = x + dx;
                if (yy >= 0 && yy < h && xx >= 0 && xx < w && rows[yy][xx] == symbol &&
                    seen.insert({yy, xx}).second)
                    todo.push({yy, xx});
            }
        }
    }
    return "";
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
