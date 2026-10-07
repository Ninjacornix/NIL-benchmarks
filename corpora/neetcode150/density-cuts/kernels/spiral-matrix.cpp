#include <cstdint>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
V kernel(I r,I c,V a){V out;I top=0,bottom=r,left=0,right=c;while(top<bottom&&left<right){for(I j=left;j<right;++j)out.push_back(a[top*c+j]);++top;for(I i=top;i<bottom;++i)out.push_back(a[i*c+right-1]);--right;if(top<bottom){for(I j=right;j>left;--j)out.push_back(a[(bottom-1)*c+j-1]);--bottom;}if(left<right){for(I i=bottom;i>top;--i)out.push_back(a[(i-1)*c+left]);++left;}}return out;}
