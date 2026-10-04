#include <fstream>
#include <iterator>
#include <algorithm>
#include <set>
#include <string>
#include <utility>
#include <vector>

std::string transform(const std::string &data) {
    std::vector<std::string> board;
    auto pos = data.find('[') + 1;
    while (data[pos] != ']') {
        auto close = data.find('"', pos + 1);
        board.push_back(data.substr(pos + 1, close - pos - 1));
        pos = close + 1;
        if (data[pos] == ',') ++pos;
    }
    int x = std::stoi(data.substr(data.find(':', pos) + 1));
    int y = std::stoi(data.substr(data.find(':', data.find(',', data.find(':', pos))) + 1));
    int height = board.size(), width = board[0].size();
    if (x < 0 || y < 0 || x >= width || y >= height) return "error\n";
    std::vector<std::pair<int, int>> todo;
    std::set<std::pair<int, int>> territory;
    std::set<char> owners;
    if (board[y][x] == ' ') { todo.push_back({x, y}); territory.insert({x, y}); }
    while (!todo.empty()) {
        auto [xx, yy] = todo.back(); todo.pop_back();
        for (auto [dx, dy] : std::vector<std::pair<int, int>>{{-1,0},{1,0},{0,-1},{0,1}}) {
            int nx = xx + dx, ny = yy + dy;
            if (nx < 0 || ny < 0 || nx >= width || ny >= height) continue;
            char cell = board[ny][nx];
            if (cell == ' ' && territory.insert({nx,ny}).second) todo.push_back({nx,ny});
            else if (cell != ' ') owners.insert(cell);
        }
    }
    std::string owner = owners == std::set<char>{'B'} ? "BLACK" : owners == std::set<char>{'W'} ? "WHITE" : "NONE";
    std::string out = "{\"owner\":\"" + owner + "\",\"territory\":[";
    for (auto [xx,yy] : territory) {
        if (out.back() != '[') out += ',';
        out += '[' + std::to_string(xx) + ',' + std::to_string(yy) + ']';
    }
    return out + "]}";
}

long long solve(const std::string &input_path, const std::string &output_path) {
    std::ifstream input(input_path,std::ios::binary);
    std::string data((std::istreambuf_iterator<char>(input)),std::istreambuf_iterator<char>());
    std::string output=transform(data);
    std::ofstream file(output_path,std::ios::binary);file.write(output.data(),output.size());
    return output.size();
}
