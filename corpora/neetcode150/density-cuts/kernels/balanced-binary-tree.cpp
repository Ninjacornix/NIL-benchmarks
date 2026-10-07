#include <algorithm>
#include <array>
#include <cstdint>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
I kernel(std::vector<std::array<I,3>> a,I root){I n=a.size();V height(n);std::vector<std::pair<I,bool>> stack;if(root!=-1)stack.emplace_back(root,false);bool okay=true;while(!stack.empty()){auto [u,ready]=stack.back();stack.pop_back();if(!ready){stack.emplace_back(u,true);for(int k=1;k<3;++k)if(a[u][k]!=-1)stack.emplace_back(a[u][k],false);}else{I l=a[u][1]==-1?0:height[a[u][1]],r=a[u][2]==-1?0:height[a[u][2]];okay&=std::abs(l-r)<=1;height[u]=std::max(l,r)+1;}}return okay;}
