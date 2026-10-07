#include <algorithm>
#include <charconv>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <queue>
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
std::string solve(Input &q){I n=q.one(),m=q.one(),s=q.one();std::vector<std::vector<std::pair<I,I>>> adj(n);for(I i=0;i<m;++i){I u=q.one(),v=q.one(),w=q.one();adj[u].emplace_back(v,w);}const I inf=1000000000000000000LL;V dist(n,inf);dist[s]=0;std::priority_queue<std::pair<I,I>,std::vector<std::pair<I,I>>,std::greater<std::pair<I,I>>> heap;heap.emplace(0,s);while(!heap.empty()){auto [d,u]=heap.top();heap.pop();if(d!=dist[u])continue;for(auto[v,w]:adj[u])if(d+w<dist[v]){dist[v]=d+w;heap.emplace(d+w,v);}}I result=*std::max_element(dist.begin(),dist.end());return scalar(result==inf?-1:result);}

int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);Input q{std::string(std::istreambuf_iterator<char>(file),{})};auto answer=solve(q);std::ofstream out(argv[2],std::ios::binary);out.write(answer.data(),answer.size());std::cout<<answer.size()<<'\n';}
