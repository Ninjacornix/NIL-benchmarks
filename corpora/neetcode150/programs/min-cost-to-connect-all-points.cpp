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
 std::vector<V> matrix(int width) { I n=one(); std::vector<V> a(n,V(width)); for(auto &r:a) for(auto &x:r)x=one(); return a; }
};
std::string scalar(I x) {return std::to_string(x)+"\n";}
std::string solve(Input &q){auto a=q.matrix(2);I n=a.size(),total=0;V dist(n,INT64_MAX);std::vector<bool>seen(n);if(n)dist[0]=0;for(I k=0;k<n;++k){I u=-1;for(I i=0;i<n;++i)if(!seen[i]&&(u==-1||dist[i]<dist[u]))u=i;total+=dist[u];seen[u]=true;for(I v=0;v<n;++v)if(!seen[v])dist[v]=std::min(dist[v],std::abs(a[u][0]-a[v][0])+std::abs(a[u][1]-a[v][1]));}return scalar(total);}

int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);Input q{std::string(std::istreambuf_iterator<char>(file),{})};auto answer=solve(q);std::ofstream out(argv[2],std::ios::binary);out.write(answer.data(),answer.size());std::cout<<answer.size()<<'\n';}
