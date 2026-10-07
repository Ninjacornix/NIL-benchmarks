#include <cstdint>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
I kernel(V a,I target){I lo=0,hi=(I)a.size()-1;while(lo<=hi){I m=(lo+hi)/2;if(a[m]==target)return m;if(a[lo]<=a[m]){if(a[lo]<=target&&target<a[m])hi=m-1;else lo=m+1;}else{if(a[m]<target&&target<=a[hi])lo=m+1;else hi=m-1;}}return -1;}
