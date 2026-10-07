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
std::string solve(Input &q){auto a=q.vector();I target=q.one(),lo=0,hi=(I)a.size()-1;while(lo<=hi){I m=(lo+hi)/2;if(a[m]==target)return scalar(m);if(a[lo]<=a[m]){if(a[lo]<=target&&target<a[m])hi=m-1;else lo=m+1;}else{if(a[m]<target&&target<=a[hi])lo=m+1;else hi=m-1;}}return scalar(-1);}

int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);Input q{std::string(std::istreambuf_iterator<char>(file),{})};auto answer=solve(q);std::ofstream out(argv[2],std::ios::binary);out.write(answer.data(),answer.size());std::cout<<answer.size()<<'\n';}
