#include <cstdint>
#include <unordered_set>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
I kernel(V a){ std::unordered_set<I> seen; for(I x:a) if(!seen.insert(x).second)return 1;return 0;}
