#include <array>
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
std::string solve(Input &q){std::istringstream in(q.data);std::string text,pattern;std::getline(in,text);std::getline(in,pattern);if(pattern.empty())return "\n";std::array<I,256> need{};for(unsigned char x:pattern)++need[x];I missing=pattern.size(),left=0,start=0,size=INT64_MAX;for(I r=0;r<(I)text.size();++r){auto x=(unsigned char)text[r];if(need[x]>0)--missing;--need[x];while(!missing){if(r-left+1<size){start=left;size=r-left+1;}auto old=(unsigned char)text[left++];if(++need[old]>0)++missing;}}return (size==INT64_MAX?"":text.substr(start,size))+"\n";}

int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);Input q{std::string(std::istreambuf_iterator<char>(file),{})};auto answer=solve(q);std::ofstream out(argv[2],std::ios::binary);out.write(answer.data(),answer.size());std::cout<<answer.size()<<'\n';}
