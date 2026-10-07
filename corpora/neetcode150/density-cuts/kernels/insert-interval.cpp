#include <algorithm>
#include <cstdint>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
std::vector<V> kernel(std::vector<V> a,I lo,I hi){std::vector<V> out;bool inserted=false;for(auto r:a){if(r[1]<lo)out.push_back(r);else if(r[0]>hi){if(!inserted){out.push_back({lo,hi});inserted=true;}out.push_back(r);}else{lo=std::min(lo,r[0]);hi=std::max(hi,r[1]);}}if(!inserted)out.push_back({lo,hi});return out;}
