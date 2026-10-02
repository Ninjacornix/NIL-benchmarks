#include <cstdint>
#include <fstream>
#include <iostream>
#include <vector>
int main(int argc,char **argv) {
    if(argc!=3) return 2;
    std::ifstream input(argv[1],std::ios::binary|std::ios::ate);
    if(!input) return 1;
    auto size=input.tellg(); if(size<0) return 1;
    std::vector<std::uint8_t> data(static_cast<std::size_t>(size));
    input.seekg(0); input.read(reinterpret_cast<char*>(data.data()),size);
    if(!input) return 1;
    for(auto &byte:data) byte=static_cast<std::uint8_t>(255-byte);
    std::ofstream output(argv[2],std::ios::binary|std::ios::trunc);
    output.write(reinterpret_cast<const char*>(data.data()),size);output.close();
    if(!output) return 1;
    std::cout<<data.size()<<'\n';
}
