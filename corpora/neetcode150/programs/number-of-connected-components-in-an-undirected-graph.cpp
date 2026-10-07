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
std::string solve(Input &q){I n=q.one(),m=q.one();V parent(n),rank(n);for(I i=0;i<n;++i)parent[i]=i;auto root=[&](I u){while(u!=parent[u]){parent[u]=parent[parent[u]];u=parent[u];}return u;};I count=n;V last;for(I i=0;i<m;++i){I u=q.one(),v=q.one(),a=root(u),b=root(v);if(a==b){last={u,v};continue;}if(rank[a]<rank[b])std::swap(a,b);parent[b]=a;--count;if(rank[a]==rank[b])++rank[a];}return scalar(count);}

int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);Input q{std::string(std::istreambuf_iterator<char>(file),{})};auto answer=solve(q);std::ofstream out(argv[2],std::ios::binary);out.write(answer.data(),answer.size());std::cout<<answer.size()<<'\n';}
