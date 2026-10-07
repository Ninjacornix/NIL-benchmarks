#include <array>
#include <cstdint>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
I kernel(std::vector<std::array<I,3>> a,I root){I n=a.size();V stack;I u=root,prev=0;bool has=false;while(u!=-1||!stack.empty()){while(u!=-1){stack.push_back(u);u=a[u][1];}u=stack.back();stack.pop_back();if(has&&a[u][0]<=prev)return 0;has=true;prev=a[u][0];u=a[u][2];}return 1;}
