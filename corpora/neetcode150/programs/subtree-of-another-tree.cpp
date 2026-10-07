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
std::string solve(Input &q){I n=q.one(),root=q.one();std::vector<std::array<I,3>> a(n);for(auto&r:a)for(auto&x:r)x=q.one();I nn=q.one(),rr=q.one();std::vector<std::array<I,3>>b(nn);for(auto&r:b)for(auto&x:r)x=q.one();if(rr==-1)return scalar(1);auto encode=[](const auto& nodes,I start){V stack{start},tokens;while(!stack.empty()){I u=stack.back();stack.pop_back();if(u==-1)tokens.push_back(INT64_MIN);else{tokens.push_back(nodes[u][0]);stack.push_back(nodes[u][2]);stack.push_back(nodes[u][1]);}}return tokens;};auto text=encode(a,root),pattern=encode(b,rr);V prefix(pattern.size());I j=0;for(I i=1;i<(I)pattern.size();++i){while(j&&pattern[i]!=pattern[j])j=prefix[j-1];if(pattern[i]==pattern[j])++j;prefix[i]=j;}j=0;for(I x:text){while(j&&x!=pattern[j])j=prefix[j-1];if(x==pattern[j])++j;if(j==(I)pattern.size())return scalar(1);}return scalar(0);}

int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);Input q{std::string(std::istreambuf_iterator<char>(file),{})};auto answer=solve(q);std::ofstream out(argv[2],std::ios::binary);out.write(answer.data(),answer.size());std::cout<<answer.size()<<'\n';}
