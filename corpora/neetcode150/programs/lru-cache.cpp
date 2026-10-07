#include <charconv>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <list>
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
std::string scalar(I x) {return std::to_string(x)+"\n";}
std::string solve(Input &q){I cap=q.one(),n=q.one();std::list<std::pair<I,I>> order;std::unordered_map<I,decltype(order)::iterator> index;std::string out;for(I i=0;i<n;++i){I op=q.one(),key=q.one();auto it=index.find(key);if(op==0){I val=q.one();if(it!=index.end()){order.erase(it->second);index.erase(it);}if(cap){order.emplace_front(key,val);index[key]=order.begin();}if((I)order.size()>cap){index.erase(order.back().first);order.pop_back();}}else if(it==index.end())out+=scalar(-1);else{I val=it->second->second;order.splice(order.begin(),order,it->second);out+=scalar(val);}}return out;}

int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);Input q{std::string(std::istreambuf_iterator<char>(file),{})};auto answer=solve(q);std::ofstream out(argv[2],std::ios::binary);out.write(answer.data(),answer.size());std::cout<<answer.size()<<'\n';}
