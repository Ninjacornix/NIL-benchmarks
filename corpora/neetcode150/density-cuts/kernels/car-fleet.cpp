#include <algorithm>
#include <cstdint>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
I kernel(I target,std::vector<V> a){std::sort(a.rbegin(),a.rend());I count=0,num=0,den=1;for(auto r:a){I d=target-r[0];if(d*den>num*r[1]){++count;num=d;den=r[1];}}return count;}
