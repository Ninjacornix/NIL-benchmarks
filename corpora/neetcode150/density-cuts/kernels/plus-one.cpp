#include <cstdint>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
V kernel(V a){I carry=1;for(I i=(I)a.size()-1;i>=0;--i){I x=a[i]+carry;a[i]=x%10;carry=x/10;}if(carry)a.insert(a.begin(),1);return a;}
