#include <charconv>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
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
std::string scalar(I x) {return std::to_string(x)+"\n";}
std::string solve(Input &q){std::istringstream in(q.data);int n;in>>n;std::string line;std::getline(in,line);std::vector<std::map<unsigned char,int>> nodes(1);std::vector<bool> terminal(1);std::string out;for(int i=0;i<n;++i){std::getline(in,line);char op=line[0];int u=0;bool present=true;for(unsigned char x:line.substr(2)){auto it=nodes[u].find(x);if(it==nodes[u].end()){if(op!='+'){present=false;break;}int next=nodes.size();nodes[u][x]=next;nodes.emplace_back();terminal.push_back(false);u=next;}else u=it->second;}if(op=='+')terminal[u]=true;else out+=scalar(present&&(op=='?'||terminal[u]));}return out;}

int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);Input q{std::string(std::istreambuf_iterator<char>(file),{})};auto answer=solve(q);std::ofstream out(argv[2],std::ios::binary);out.write(answer.data(),answer.size());std::cout<<answer.size()<<'\n';}
