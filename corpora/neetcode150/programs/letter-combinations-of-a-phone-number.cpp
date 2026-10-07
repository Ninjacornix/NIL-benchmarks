#include <array>
#include <charconv>
#include <cstdint>
#include <fstream>
#include <functional>
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
std::string solve(Input &q){if(q.data.empty())return "";std::array<std::string,8> letters={"abc","def","ghi","jkl","mno","pqrs","tuv","wxyz"};std::string out;std::function<void(int,std::string)> visit=[&](int i,std::string prefix){if(i==(int)q.data.size()){out+=prefix+'\n';return;}for(char c:letters[q.data[i]-'2'])visit(i+1,prefix+c);};visit(0,"");return out;}

int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);Input q{std::string(std::istreambuf_iterator<char>(file),{})};auto answer=solve(q);std::ofstream out(argv[2],std::ios::binary);out.write(answer.data(),answer.size());std::cout<<answer.size()<<'\n';}
