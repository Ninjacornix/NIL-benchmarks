#include <algorithm>
#include <cstdint>
#include <stdexcept>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
I kernel(V a,V b){if(a.size()>b.size())std::swap(a,b);I lo=0,hi=a.size(),half=(a.size()+b.size()+1)/2;const I inf=INT64_MAX;while(lo<=hi){I i=(lo+hi)/2,j=half-i,al=i?a[i-1]:-inf,ar=i<(I)a.size()?a[i]:inf,bl=j?b[j-1]:-inf,br=j<(I)b.size()?b[j]:inf;if(al>br)hi=i-1;else if(bl>ar)lo=i+1;else return (a.size()+b.size())%2?2*std::max(al,bl):std::max(al,bl)+std::min(ar,br);}throw std::runtime_error("partition");}
