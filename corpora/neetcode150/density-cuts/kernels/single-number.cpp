#include <cstdint>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
I kernel(V a){I result=0;for(I x:a)result^=x;return result;}
