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
};
std::string row(const V &a) {std::string s; for(std::size_t i=0;i<a.size();++i) {if(i)s+=' ';s+=std::to_string(a[i]);}return s+'\n';}
std::string solve(Input &q){std::priority_queue<I>low;std::priority_queue<I,V,std::greater<I>>high;V out;for(I x:q.vector()){low.push(x);high.push(low.top());low.pop();if(high.size()>low.size()){low.push(high.top());high.pop();}out.push_back(low.size()>high.size()?2*low.top():low.top()+high.top());}return row(out);}

int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);Input q{std::string(std::istreambuf_iterator<char>(file),{})};auto answer=solve(q);std::ofstream out(argv[2],std::ios::binary);out.write(answer.data(),answer.size());std::cout<<answer.size()<<'\n';}
