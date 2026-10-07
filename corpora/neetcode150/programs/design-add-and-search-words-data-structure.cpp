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
std::string solve(Input &q){std::istringstream in(q.data);I n;in>>n;std::string line,out;std::getline(in,line);std::vector<std::map<char,I>>trie(1);std::vector<bool>end(1);for(I i=0;i<n;++i){std::getline(in,line);char op=line[0];auto word=line.substr(2);if(op=='+'){I u=0;for(char x:word){auto it=trie[u].find(x);if(it==trie[u].end()){I next=trie.size();trie[u][x]=next;trie.emplace_back();end.push_back(false);u=next;}else u=it->second;}end[u]=true;}else{V frontier{0};for(char x:word){V next;for(I u:frontier)for(auto[c,v]:trie[u])if(x=='.'||x==c)next.push_back(v);frontier=next;}bool found=false;for(I u:frontier)found|=end[u];out+=scalar(found);}}return out;}

int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);Input q{std::string(std::istreambuf_iterator<char>(file),{})};auto answer=solve(q);std::ofstream out(argv[2],std::ios::binary);out.write(answer.data(),answer.size());std::cout<<answer.size()<<'\n';}
