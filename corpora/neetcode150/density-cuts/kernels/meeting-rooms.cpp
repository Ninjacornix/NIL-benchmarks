#include <algorithm>
#include <cstdint>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
I kernel(std::vector<V> a){std::sort(a.begin(),a.end());for(std::size_t i=1;i<a.size();++i)if(a[i-1][1]>a[i][0])return 0;return 1;}
