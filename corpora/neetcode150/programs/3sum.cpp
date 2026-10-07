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
std::string row(const V &a) {std::string s; for(std::size_t i=0;i<a.size();++i) {if(i)s+=' ';s+=std::to_string(a[i]);}return s+'\n';}
std::string rows(const std::vector<V>& a) {std::string s;for(const auto &r:a)s+=row(r);return s;}
std::string solve(Input &q){auto a=q.vector();std::sort(a.begin(),a.end());std::vector<V> out;for(int i=0;i+2<(int)a.size();++i){if(i&&a[i]==a[i-1])continue;int l=i+1,r=a.size()-1;while(l<r){I s=a[i]+a[l]+a[r];if(s<0)++l;else if(s>0)--r;else{out.push_back({a[i],a[l],a[r]});++l;--r;while(l<r&&a[l]==a[l-1])++l;while(l<r&&a[r]==a[r+1])--r;}}}return rows(out);}

int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);Input q{std::string(std::istreambuf_iterator<char>(file),{})};auto answer=solve(q);std::ofstream out(argv[2],std::ios::binary);out.write(answer.data(),answer.size());std::cout<<answer.size()<<'\n';}
