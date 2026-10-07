#include <charconv>
#include <cstdint>
#include <fstream>
#include <functional>
#include <iostream>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
using I = std::int64_t;
using V = std::vector<I>;
struct Input {
 std::string data; std::size_t cursor=0;
 I one() { while(cursor<data.size() && data[cursor]<=32) ++cursor; I x=0;
 auto result=std::from_chars(data.data()+cursor,data.data()+data.size(),x);
 if(result.ec!=std::errc()) throw std::runtime_error("bad fixture"); cursor=result.ptr-data.data(); return x; }
};
std::string row(const V &a) {std::string s; for(std::size_t i=0;i<a.size();++i) {if(i)s+=' ';s+=std::to_string(a[i]);}return s+'\n';}
std::string solve(Input &q){int n=q.one();V path;std::string out;std::set<int> columns,down,up;std::function<void(int)> visit=[&](int r){if(r==n){out+=row(path);return;}for(int c=0;c<n;++c)if(!columns.count(c)&&!down.count(r-c)&&!up.count(r+c)){path.push_back(c);columns.insert(c);down.insert(r-c);up.insert(r+c);visit(r+1);up.erase(r+c);down.erase(r-c);columns.erase(c);path.pop_back();}};visit(0);return out;}

int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);Input q{std::string(std::istreambuf_iterator<char>(file),{})};auto answer=solve(q);std::ofstream out(argv[2],std::ios::binary);out.write(answer.data(),answer.size());std::cout<<answer.size()<<'\n';}
