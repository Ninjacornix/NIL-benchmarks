#include <charconv>
#include <cstdint>
#include <fstream>
#include <iostream>
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
std::string solve(Input &q){std::istringstream in(q.data);std::string a,b;std::getline(in,a);std::getline(in,b);V out(a.size()+b.size());for(I i=(I)a.size()-1;i>=0;--i)for(I j=(I)b.size()-1;j>=0;--j){I x=out[i+j+1]+(a[i]-'0')*(b[j]-'0');out[i+j+1]=x%10;out[i+j]+=x/10;}std::string s;for(I x:out)if(x||!s.empty())s+=char('0'+x);return (s.empty()?"0":s)+'\n';}

int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);Input q{std::string(std::istreambuf_iterator<char>(file),{})};auto answer=solve(q);std::ofstream out(argv[2],std::ios::binary);out.write(answer.data(),answer.size());std::cout<<answer.size()<<'\n';}
