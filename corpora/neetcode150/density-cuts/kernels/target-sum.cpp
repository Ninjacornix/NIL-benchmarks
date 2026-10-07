#include <cstdint>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
I kernel(V a,I target){I total=0;for(I x:a)total+=x;V dp(2*total+1);dp[total]=1;for(I x:a){V next(dp.size());for(I i=0;i<(I)dp.size();++i)if(dp[i]){next[i+x]+=dp[i];next[i-x]+=dp[i];}dp=std::move(next);}return target < -total || target>total?0:dp[total+target];}
