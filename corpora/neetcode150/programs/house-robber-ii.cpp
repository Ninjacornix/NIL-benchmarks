#include <algorithm>
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
 V vector() { I n=one(); V a(n); for(auto &x:a) x=one(); return a; }
};
std::string scalar(I x) {return std::to_string(x)+"\n";}
std::string solve(Input &q){auto a=q.vector();if(a.size()==1)return scalar(a[0]);auto run=[&](I l,I r){I skip=0,take=0;for(I i=l;i<r;++i){I next=std::max(skip,take);take=skip+a[i];skip=next;}return std::max(skip,take);};return scalar(std::max(run(0,a.empty()?0:a.size()-1),run(a.empty()?0:1,a.size())));}

int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);Input q{std::string(std::istreambuf_iterator<char>(file),{})};auto answer=solve(q);std::ofstream out(argv[2],std::ios::binary);out.write(answer.data(),answer.size());std::cout<<answer.size()<<'\n';}
