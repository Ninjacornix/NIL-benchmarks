#include <algorithm>
#include <cstdint>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
I kernel(V coins,I amount){V dp(amount+1,amount+1);dp[0]=0;for(I i=1;i<=amount;++i)for(I c:coins)if(c<=i)dp[i]=std::min(dp[i],dp[i-c]+1);return dp[amount]>amount?-1:dp[amount];}
#include <fstream>
#include <iostream>
#include <sstream>
struct Input {std::string data;std::istringstream input;I one(){I x;input>>x;return x;}V vector(){V a(one());for(auto&x:a)x=one();return a;}std::vector<V> matrix(int w){std::vector<V>a(one(),V(w));for(auto&r:a)for(auto&x:r)x=one();return a;}};
std::string row(const V&a){std::string s;for(I x:a){if(!s.empty())s+=' ';s+=std::to_string(x);}return s+'\n';}
int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);auto raw_input=std::string(std::istreambuf_iterator<char>(file),{});Input q{raw_input,std::istringstream(raw_input)};auto coins=q.vector();I amount=q.one();auto result=kernel(coins,amount);auto answer=std::to_string(result)+'\n';std::ofstream out(argv[2],std::ios::binary);out<<answer;std::cout<<answer.size()<<'\n';}
