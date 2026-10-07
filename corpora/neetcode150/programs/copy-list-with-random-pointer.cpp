#include <charconv>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <unordered_map>
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
std::string rows(const std::vector<V>& a) {std::string s;for(const auto &r:a)s+=row(r);return s;}
std::string solve(Input &q){I n=q.one(),head=q.one();std::vector<V>a(n,V(3));for(auto&r:a)for(auto&x:r)x=q.one();V order;while(head!=-1){order.push_back(head);head=a[head][1];}std::unordered_map<I,I> index;index[-1]=-1;for(I i=0;i<(I)order.size();++i)index[order[i]]=i;std::vector<V> out;for(I u:order)out.push_back({a[u][0],index[a[u][1]],index[a[u][2]]});return rows(out);}

int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);Input q{std::string(std::istreambuf_iterator<char>(file),{})};auto answer=solve(q);std::ofstream out(argv[2],std::ios::binary);out.write(answer.data(),answer.size());std::cout<<answer.size()<<'\n';}
