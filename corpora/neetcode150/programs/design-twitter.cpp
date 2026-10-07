#include <array>
#include <charconv>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <queue>
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
std::string row(const V &a) {std::string s; for(std::size_t i=0;i<a.size();++i) {if(i)s+=' ';s+=std::to_string(a[i]);}return s+'\n';}
std::string solve(Input &q){std::istringstream in(q.data);I n,clock=0;in>>n;std::map<I,std::set<I>>follow;std::map<I,std::vector<std::pair<I,I>>>posts;std::string out;for(I i=0;i<n;++i){std::string op;I u,v;in>>op>>u;if(op=="post"){in>>v;posts[u].emplace_back(clock++,v);}else if(op=="follow"){in>>v;follow[u].insert(v);}else if(op=="unfollow"){in>>v;follow[u].erase(v);}else{auto who=follow[u];who.insert(u);using T=std::array<I,3>;std::priority_queue<T>heap;for(I w:who)if(!posts[w].empty())heap.push({posts[w].back().first,w,I(posts[w].size()-1)});V feed;while(!heap.empty()&&feed.size()<10){auto[t,w,j]=heap.top();heap.pop();feed.push_back(posts[w][j].second);if(j)heap.push({posts[w][j-1].first,w,j-1});}out+=row(feed);}}return out;}

int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);Input q{std::string(std::istreambuf_iterator<char>(file),{})};auto answer=solve(q);std::ofstream out(argv[2],std::ios::binary);out.write(answer.data(),answer.size());std::cout<<answer.size()<<'\n';}
