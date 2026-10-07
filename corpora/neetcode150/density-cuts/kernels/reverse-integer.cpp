#include <cstdint>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
V kernel(V a){V out;for(I x:a){I r=0;while(x){r=r*10+x%10;x/=10;}out.push_back(r<INT32_MIN||r>INT32_MAX?0:r);}return out;}
