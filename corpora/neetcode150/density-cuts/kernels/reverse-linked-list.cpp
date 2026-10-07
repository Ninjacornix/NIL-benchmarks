#include <algorithm>
#include <array>
#include <cstdint>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
V kernel(std::vector<std::array<I,2>> a,I head){V out;while(head!=-1){out.push_back(a[head][0]);head=a[head][1];}std::reverse(out.begin(),out.end());return out;}
