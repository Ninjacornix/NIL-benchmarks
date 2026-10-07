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
std::string solve(Input &q){I best_l=0,best_r=0,count=0;for(I center=0;center<2*(I)q.data.size()-1;++center){I l=center/2,r=l+center%2;while(l>=0&&r<(I)q.data.size()&&q.data[l]==q.data[r]){++count;if(r-l+1>best_r-best_l||(r-l+1==best_r-best_l&&l<best_l)){best_l=l;best_r=r+1;}--l;++r;}}return q.data.substr(best_l,best_r-best_l)+'\n';}

int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);Input q{std::string(std::istreambuf_iterator<char>(file),{})};auto answer=solve(q);std::ofstream out(argv[2],std::ios::binary);out.write(answer.data(),answer.size());std::cout<<answer.size()<<'\n';}
