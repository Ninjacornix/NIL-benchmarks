#include <algorithm>
#include <array>
#include <cstdint>
#include <string>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
I kernel(I k,std::string data){std::array<I,26> count{};I left=0,best=0,peak=0;for(I i=0;i<(I)(data.size());++i){peak=std::max(peak,++count[data[i]-'A']);if(i-left+1-peak>k)--count[data[left++]-'A'];best=std::max(best,i-left+1);}return best;}
