#include <cstdint>
#include <fstream>
#include <iostream>
#include <iterator>
#include <string>
#include <vector>
int main(int argc,char **argv) {
    if(argc<3) return 2;
    std::string mode=argv[1];
    if(mode=="newlines") {
        std::ifstream input(argv[2],std::ios::binary|std::ios::ate);
        if(!input) return 1;
        auto size=input.tellg(); if(size<0) return 1;
        std::string data(static_cast<std::size_t>(size), '\0');
        input.seekg(0);input.read(data.data(),size);if(!input) return 1;
        std::int64_t count=0;for(unsigned char byte:data) count+=byte==10;
        std::cout<<count<<'\n';
    } else {
        auto n=std::stoll(argv[2]); if(n<0) return 2;
        if(mode=="reduce") {
            std::vector<std::int64_t> data(static_cast<std::size_t>(n),1);
            std::int64_t total=0;for(auto value:data) total+=value;
            std::cout<<total<<'\n';
        } else if(mode=="append" || mode=="report") {
            std::string data;
            if(mode=="append") {
                for(std::int64_t i=0;i<n;i++) data.push_back('x');
            } else {
                for(std::int64_t i=0;i<n;i++) { data+=std::to_string(i);data.push_back('\n'); }
            }
            if(mode=="report") {
                if(argc!=4) return 2;
                std::ofstream out(argv[3],std::ios::binary|std::ios::trunc);
                out.write(data.data(),static_cast<std::streamsize>(data.size()));out.close();if(!out) return 1;
            }
            std::cout<<data.size()<<'\n';
        } else return 2;
    }
}
