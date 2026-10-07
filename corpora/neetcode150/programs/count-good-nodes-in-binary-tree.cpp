#include <algorithm>
#include <array>
#include <charconv>
#include <cstdint>
#include <fstream>
#include <iostream>
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
std::string scalar(I x) {return std::to_string(x)+"\n";}
std::string solve(Input &q){I n=q.one(),root=q.one();std::vector<std::array<I,3>> a(n);for(auto&r:a)for(auto&x:r)x=q.one();std::vector<std::pair<I,I>> stack;if(root!=-1)stack.emplace_back(root,INT64_MIN);I count=0;while(!stack.empty()){auto[u,p]=stack.back();stack.pop_back();count+=a[u][0]>=p;for(int k=1;k<3;++k)if(a[u][k]!=-1)stack.emplace_back(a[u][k],std::max(p,a[u][0]));}return scalar(count);}

int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);Input q{std::string(std::istreambuf_iterator<char>(file),{})};auto answer=solve(q);std::ofstream out(argv[2],std::ios::binary);out.write(answer.data(),answer.size());std::cout<<answer.size()<<'\n';}
