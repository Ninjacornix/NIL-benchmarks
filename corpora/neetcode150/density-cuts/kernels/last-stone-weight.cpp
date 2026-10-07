#include <cstdint>
#include <queue>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
I kernel(V a){std::priority_queue<I> h(a.begin(),a.end());while(h.size()>1){I x=h.top();h.pop();I y=h.top();h.pop();if(x!=y)h.push(x-y);}return h.empty()?0:h.top();}
