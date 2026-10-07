#include <cstdint>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
I kernel(V gas,V cost){I prefix=0,low=0,start=0;for(I i=0;i<(I)gas.size();++i){prefix+=gas[i]-cost[i];if(prefix<low){low=prefix;start=i+1;}}return gas.empty()||prefix<0?-1:start;}
