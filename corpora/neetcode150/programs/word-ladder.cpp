#include <charconv>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <queue>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
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
std::string solve(Input &q){std::istringstream in(q.data);std::string start,end;std::getline(in,start);std::getline(in,end);I n;in>>n;std::unordered_set<std::string>dict;for(I i=0;i<n;++i){std::string w;in>>w;dict.insert(w);}if(!dict.count(end))return scalar(0);dict.insert(start);std::unordered_map<std::string,std::vector<std::string>>patterns;for(auto&w:dict)for(std::size_t i=0;i<w.size();++i){auto key=w;key[i]='*';patterns[key].push_back(w);}std::queue<std::pair<std::string,I>>queue;queue.emplace(start,1);std::unordered_set<std::string>seen{start};while(!queue.empty()){auto[w,d]=queue.front();queue.pop();if(w==end)return scalar(d);for(std::size_t i=0;i<w.size();++i){auto key=w;key[i]='*';auto it=patterns.find(key);if(it==patterns.end())continue;for(auto&v:it->second)if(seen.insert(v).second)queue.emplace(v,d+1);patterns.erase(it);}}return scalar(0);}

int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);Input q{std::string(std::istreambuf_iterator<char>(file),{})};auto answer=solve(q);std::ofstream out(argv[2],std::ios::binary);out.write(answer.data(),answer.size());std::cout<<answer.size()<<'\n';}
