#include <algorithm>
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
std::string solve(Input &q){std::istringstream in(q.data);std::string text,p;std::getline(in,text);std::getline(in,p);std::vector<bool>dp(p.size()+1);dp[0]=true;for(std::size_t j=2;j<=p.size();++j)if(p[j-1]=='*')dp[j]=dp[j-2];for(char x:text){auto prev=dp;std::fill(dp.begin(),dp.end(),false);for(std::size_t j=1;j<=p.size();++j){if(p[j-1]=='*')dp[j]=dp[j-2]||(prev[j]&&(p[j-2]=='.'||p[j-2]==x));else dp[j]=prev[j-1]&&(p[j-1]=='.'||p[j-1]==x);}}return scalar(dp.back());}

int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);Input q{std::string(std::istreambuf_iterator<char>(file),{})};auto answer=solve(q);std::ofstream out(argv[2],std::ios::binary);out.write(answer.data(),answer.size());std::cout<<answer.size()<<'\n';}
