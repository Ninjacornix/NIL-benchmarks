#include <algorithm>
#include <cstdint>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
I kernel(V coins,I amount){V dp(amount+1,amount+1);dp[0]=0;for(I i=1;i<=amount;++i)for(I c:coins)if(c<=i)dp[i]=std::min(dp[i],dp[i-c]+1);return dp[amount]>amount?-1:dp[amount];}
