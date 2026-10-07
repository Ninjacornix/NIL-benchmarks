#include <cstdint>
#include <queue>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
I kernel(I n,std::vector<V> edges){std::vector<V> adj(n);V degree(n);for(auto edge:edges){I u=edge[0],v=edge[1];adj[u].push_back(v);++degree[v];}std::priority_queue<I,V,std::greater<I>> heap;for(I i=0;i<n;++i)if(!degree[i])heap.push(i);V out;while(!heap.empty()){I u=heap.top();heap.pop();out.push_back(u);for(I v:adj[u])if(--degree[v]==0)heap.push(v);}return (I)out.size()==n;}
#include <fstream>
#include <iostream>
#include <sstream>
struct Input {std::string data;std::istringstream input;I one(){I x;input>>x;return x;}V vector(){V a(one());for(auto&x:a)x=one();return a;}std::vector<V> matrix(int w){std::vector<V>a(one(),V(w));for(auto&r:a)for(auto&x:r)x=one();return a;}};
std::string row(const V&a){std::string s;for(I x:a){if(!s.empty())s+=' ';s+=std::to_string(x);}return s+'\n';}
int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);auto raw_input=std::string(std::istreambuf_iterator<char>(file),{});Input q{raw_input,std::istringstream(raw_input)};I n=q.one(),m=q.one();std::vector<V> edges(m,V(2));for(auto&r:edges)for(auto&x:r)x=q.one();auto result=kernel(n,edges);auto answer=std::to_string(result)+'\n';std::ofstream out(argv[2],std::ios::binary);out<<answer;std::cout<<answer.size()<<'\n';}
