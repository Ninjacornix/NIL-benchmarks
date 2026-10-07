#include <charconv>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <iterator>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>
using I = std::int64_t;
using V = std::vector<I>;
struct Input {
 std::string data; std::size_t cursor=0;
 I one() { while(cursor<data.size() && data[cursor]<=32) ++cursor; I x=0;
 auto result=std::from_chars(data.data()+cursor,data.data()+data.size(),x);
 if(result.ec!=std::errc()) throw std::runtime_error("bad fixture"); cursor=result.ptr-data.data(); return x; }
};
std::string solve(Input &q){std::istringstream in(q.data);I n;in>>n;std::unordered_map<std::string,std::vector<std::pair<I,std::string>>> table;std::string op,key,value,out;for(I i=0;i<n;++i){I t;in>>op>>key>>t;if(op=="set"){in>>value;table[key].emplace_back(t,value);}else{auto&entries=table[key];auto it=std::upper_bound(entries.begin(),entries.end(),std::make_pair(t,std::string(1,char(127))));out+=(it==entries.begin()?"":std::prev(it)->second)+"\n";}}return out;}

int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);Input q{std::string(std::istreambuf_iterator<char>(file),{})};auto answer=solve(q);std::ofstream out(argv[2],std::ios::binary);out.write(answer.data(),answer.size());std::cout<<answer.size()<<'\n';}
