#include <algorithm>
#include <charconv>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
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
std::string solve(Input &q){std::istringstream in(q.data);I n;in>>n;std::map<std::string,std::vector<std::string>>adj;for(I i=0;i<n;++i){std::string a,b;in>>a>>b;adj[a].push_back(b);}for(auto&[key,a]:adj)std::sort(a.rbegin(),a.rend());std::vector<std::string>stack{"AAA"},out;while(!stack.empty()){auto&edges=adj[stack.back()];if(!edges.empty()){auto next=edges.back();edges.pop_back();stack.push_back(next);}else{out.push_back(stack.back());stack.pop_back();}}std::reverse(out.begin(),out.end());std::string s;for(std::size_t i=0;i<out.size();++i){if(i)s+=' ';s+=out[i];}return s+'\n';}

int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);Input q{std::string(std::istreambuf_iterator<char>(file),{})};auto answer=solve(q);std::ofstream out(argv[2],std::ios::binary);out.write(answer.data(),answer.size());std::cout<<answer.size()<<'\n';}
