#include <algorithm>
#include <cstdint>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
I kernel(V a,I k){std::sort(a.begin(),a.end());return a[a.size()-k];}
