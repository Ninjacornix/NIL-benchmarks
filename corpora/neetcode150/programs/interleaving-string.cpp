#include <charconv>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <sstream>
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
std::string solve(Input &q){std::istringstream in(q.data);std::string a,b,c;std::getline(in,a);std::getline(in,b);std::getline(in,c);if(a.size()+b.size()!=c.size())return scalar(0);std::vector<bool>dp(b.size()+1);dp[0]=true;for(std::size_t j=1;j<=b.size();++j)dp[j]=dp[j-1]&&b[j-1]==c[j-1];for(std::size_t i=1;i<=a.size();++i){dp[0]=dp[0]&&a[i-1]==c[i-1];for(std::size_t j=1;j<=b.size();++j)dp[j]=(dp[j]&&a[i-1]==c[i+j-1])||(dp[j-1]&&b[j-1]==c[i+j-1]);}return scalar(dp.back());}

int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);Input q{std::string(std::istreambuf_iterator<char>(file),{})};auto answer=solve(q);std::ofstream out(argv[2],std::ios::binary);out.write(answer.data(),answer.size());std::cout<<answer.size()<<'\n';}
