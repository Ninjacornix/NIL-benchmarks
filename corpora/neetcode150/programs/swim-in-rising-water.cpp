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
std::string solve(Input &q){I r=q.one(),c=r;V a(r*r);for(auto&x:a)x=q.one();auto neighbours=[&](I u){V v;if(u/c)v.push_back(u-c);if(u/c+1<r)v.push_back(u+c);if(u%c)v.push_back(u-1);if(u%c+1<c)v.push_back(u+1);return v;};V dist(a.size(),INT64_MAX);dist[0]=a[0];using P=std::pair<I,I>;std::priority_queue<P,std::vector<P>,std::greater<P>>heap;heap.emplace(a[0],0);while(!heap.empty()){auto[d,u]=heap.top();heap.pop();if(u==(I)a.size()-1)return scalar(d);if(d!=dist[u])continue;for(I v:neighbours(u)){I next=std::max(d,a[v]);if(next<dist[v]){dist[v]=next;heap.emplace(next,v);}}}throw std::runtime_error("path");}

int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);Input q{std::string(std::istreambuf_iterator<char>(file),{})};auto answer=solve(q);std::ofstream out(argv[2],std::ios::binary);out.write(answer.data(),answer.size());std::cout<<answer.size()<<'\n';}
