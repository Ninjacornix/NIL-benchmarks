#include <algorithm>
#include <charconv>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <queue>
#include <set>
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
std::string solve(Input &q){std::istringstream in(q.data);I n;in>>n;std::vector<std::string>words(n);std::map<char,std::set<char>>adj;std::map<char,I>degree;for(auto&w:words){in>>w;for(char x:w){adj[x];degree[x];}}for(I i=1;i<n;++i){auto&a=words[i-1];auto&b=words[i];std::size_t j=0;while(j<std::min(a.size(),b.size())&&a[j]==b[j])++j;if(j==std::min(a.size(),b.size())){if(a.size()>b.size())return "-1\n";}else if(adj[a[j]].insert(b[j]).second)++degree[b[j]];}std::priority_queue<char,std::vector<char>,std::greater<char>>heap;for(auto[x,d]:degree)if(!d)heap.push(x);std::string out;while(!heap.empty()){char u=heap.top();heap.pop();out+=u;for(char v:adj[u])if(--degree[v]==0)heap.push(v);}return (out.size()==adj.size()?out:"-1")+'\n';}

int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);Input q{std::string(std::istreambuf_iterator<char>(file),{})};auto answer=solve(q);std::ofstream out(argv[2],std::ios::binary);out.write(answer.data(),answer.size());std::cout<<answer.size()<<'\n';}
