// Shared execution adapter excluded from all solution counts.
#include <iostream>
#include <string>
long long solve(const std::string&, const std::string&);
int main() {
    std::cout << solve("input.bin", "output.bin") << '\n';
}
