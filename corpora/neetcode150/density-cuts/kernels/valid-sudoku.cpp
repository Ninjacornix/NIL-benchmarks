#include <array>
#include <cstdint>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
I kernel(V a){std::array<int,9> rs{},cs{},bs{};for(int i=0;i<81;++i){int x=a[i];if(!x)continue;int b=(i/27)*3+(i%9)/3,bit=1<<x;if((rs[i/9]|cs[i%9]|bs[b])&bit)return 0;rs[i/9]|=bit;cs[i%9]|=bit;bs[b]|=bit;}return 1;}
