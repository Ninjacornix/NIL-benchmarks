#include <algorithm>
#include <cstdint>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
I kernel(V a){I hold=-1000000000000000000LL,sold=hold,rest=0;for(I p:a){I h=std::max(hold,rest-p),s=hold+p,r=std::max(rest,sold);hold=h;sold=s;rest=r;}return std::max(rest,sold);}
