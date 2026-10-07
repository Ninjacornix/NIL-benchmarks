#include <array>
#include <charconv>
#include <cstdint>
#include <fstream>
#include <functional>
#include <iostream>
#include <map>
#include <set>
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
std::string solve(Input &q){std::istringstream in(q.data);int r,c;in>>r>>c;std::vector<std::string> board(r);for(auto&x:board)in>>x;int nw;in>>nw;std::vector<std::map<char,int>> trie(1);std::vector<int> end(1,-1);std::vector<std::string> words(nw);for(int i=0;i<nw;++i){in>>words[i];int u=0;for(char x:words[i]){auto it=trie[u].find(x);if(it==trie[u].end()){int next=trie.size();trie[u][x]=next;trie.emplace_back();end.push_back(-1);u=next;}else u=it->second;}end[u]=i;}std::set<std::string> found;std::function<void(int,int,int)> visit=[&](int i,int j,int u){char x=board[i][j];auto it=trie[u].find(x);if(it==trie[u].end())return;int v=it->second;if(end[v]!=-1)found.insert(words[end[v]]);board[i][j]=0;for(auto [di,dj]:std::array<std::pair<int,int>,4>{{{-1,0},{1,0},{0,-1},{0,1}}}){int a=i+di,b=j+dj;if(a>=0&&a<r&&b>=0&&b<c&&board[a][b])visit(a,b,v);}board[i][j]=x;};for(int i=0;i<r;++i)for(int j=0;j<c;++j)visit(i,j,0);std::string out;for(auto&w:found)out+=w+'\n';return out;}

int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);Input q{std::string(std::istreambuf_iterator<char>(file),{})};auto answer=solve(q);std::ofstream out(argv[2],std::ios::binary);out.write(answer.data(),answer.size());std::cout<<answer.size()<<'\n';}
