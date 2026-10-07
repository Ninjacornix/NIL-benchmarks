#include <algorithm>
#include <cstdint>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
I kernel(V a){I running=a[0],best=running;for(std::size_t i=1;i<a.size();++i){running=std::max(a[i],running+a[i]);best=std::max(best,running);}return best;}
