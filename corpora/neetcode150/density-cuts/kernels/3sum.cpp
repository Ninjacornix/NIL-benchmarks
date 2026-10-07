#include <algorithm>
#include <cstdint>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
std::vector<V> kernel(V a){std::sort(a.begin(),a.end());std::vector<V> out;for(int i=0;i+2<(int)a.size();++i){if(i&&a[i]==a[i-1])continue;int l=i+1,r=a.size()-1;while(l<r){I s=a[i]+a[l]+a[r];if(s<0)++l;else if(s>0)--r;else{out.push_back({a[i],a[l],a[r]});++l;--r;while(l<r&&a[l]==a[l-1])++l;while(l<r&&a[r]==a[r+1])--r;}}}return out;}
