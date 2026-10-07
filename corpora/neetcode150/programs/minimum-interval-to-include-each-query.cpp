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
 V vector() { I n=one(); V a(n); for(auto &x:a) x=one(); return a; }
 std::vector<V> matrix(int width) { I n=one(); std::vector<V> a(n,V(width)); for(auto &r:a) for(auto &x:r)x=one(); return a; }
};
std::string row(const V &a) {std::string s; for(std::size_t i=0;i<a.size();++i) {if(i)s+=' ';s+=std::to_string(a[i]);}return s+'\n';}
std::string solve(Input &q){auto a=q.matrix(2);auto queries=q.vector();std::sort(a.begin(),a.end());std::vector<std::pair<I,I>>sorted;for(I i=0;i<(I)queries.size();++i)sorted.emplace_back(queries[i],i);std::sort(sorted.begin(),sorted.end());using P=std::pair<I,I>;std::priority_queue<P,std::vector<P>,std::greater<P>>heap;V out(queries.size(),-1);I i=0;for(auto[x,j]:sorted){while(i<(I)a.size()&&a[i][0]<=x){heap.emplace(a[i][1]-a[i][0]+1,a[i][1]);++i;}while(!heap.empty()&&heap.top().second<x)heap.pop();if(!heap.empty())out[j]=heap.top().first;}return row(out);}

int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);Input q{std::string(std::istreambuf_iterator<char>(file),{})};auto answer=solve(q);std::ofstream out(argv[2],std::ios::binary);out.write(answer.data(),answer.size());std::cout<<answer.size()<<'\n';}
