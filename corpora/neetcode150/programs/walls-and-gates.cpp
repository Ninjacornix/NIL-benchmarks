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
std::string row(const V &a) {std::string s; for(std::size_t i=0;i<a.size();++i) {if(i)s+=' ';s+=std::to_string(a[i]);}return s+'\n';}
std::string solve(Input &q){I r=q.one(),c=q.one();V a(r*c);for(auto&x:a)x=q.one();auto neighbours=[&](I u){V v;I i=u/c,j=u%c;if(i)v.push_back(u-c);if(i+1<r)v.push_back(u+c);if(j)v.push_back(u-1);if(j+1<c)v.push_back(u+1);return v;};V dist(a.size(),2147483647);std::queue<I>queue;for(I u=0;u<r*c;++u){if(a[u]==-1)dist[u]=-1;if(a[u]==0){dist[u]=0;queue.push(u);}}while(!queue.empty()){I u=queue.front();queue.pop();for(I v:neighbours(u))if(dist[v]==2147483647){dist[v]=dist[u]+1;queue.push(v);}}return row(dist);}

int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);Input q{std::string(std::istreambuf_iterator<char>(file),{})};auto answer=solve(q);std::ofstream out(argv[2],std::ios::binary);out.write(answer.data(),answer.size());std::cout<<answer.size()<<'\n';}
