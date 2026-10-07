#include <algorithm>
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
std::string solve(Input &q){auto text=q.data;if(!text.empty()&&text.back()=='\n')text.pop_back();std::vector<std::string>out;std::function<void(int,std::string)>visit=[&](int i,std::string path){if(i==(int)text.size()){out.push_back(path);return;}for(int j=i+1;j<=(int)text.size();++j){auto s=text.substr(i,j-i),rev=s;std::reverse(rev.begin(),rev.end());if(s==rev)visit(j,path+(path.empty()?"":" ")+s);}};visit(0,"");std::sort(out.begin(),out.end());std::string answer;for(auto&s:out)answer+=s+'\n';return answer;}

int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);Input q{std::string(std::istreambuf_iterator<char>(file),{})};auto answer=solve(q);std::ofstream out(argv[2],std::ios::binary);out.write(answer.data(),answer.size());std::cout<<answer.size()<<'\n';}
