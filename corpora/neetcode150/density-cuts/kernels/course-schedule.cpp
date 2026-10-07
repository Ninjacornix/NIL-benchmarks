#include <cstdint>
#include <queue>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
I kernel(I n,std::vector<V> edges){std::vector<V> adj(n);V degree(n);for(auto edge:edges){I u=edge[0],v=edge[1];adj[u].push_back(v);++degree[v];}std::priority_queue<I,V,std::greater<I>> heap;for(I i=0;i<n;++i)if(!degree[i])heap.push(i);V out;while(!heap.empty()){I u=heap.top();heap.pop();out.push_back(u);for(I v:adj[u])if(--degree[v]==0)heap.push(v);}return (I)out.size()==n;}
