#include <algorithm>
#include <array>
#include <cstdint>
#include <string>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
I kernel(std::string data){std::array<I,256> last;last.fill(-1);I left=0,best=0;for(I i=0;i<(I)data.size();++i){auto x=(unsigned char)data[i];left=std::max(left,last[x]+1);last[x]=i;best=std::max(best,i-left+1);}return best;}
