#include <algorithm>
#include <cstdint>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
I kernel(V a){I x=0,y=0;for(I cost:a){I next=cost+std::min(x,y);x=y;y=next;}return std::min(x,y);}
