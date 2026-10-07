#include <algorithm>
#include <array>
#include <cstdint>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
I kernel(std::vector<std::array<I,3>> a,I root){I n=a.size();V height(n);std::vector<std::pair<I,bool>> stack;if(root!=-1)stack.emplace_back(root,false);bool okay=true;while(!stack.empty()){auto [u,ready]=stack.back();stack.pop_back();if(!ready){stack.emplace_back(u,true);for(int k=1;k<3;++k)if(a[u][k]!=-1)stack.emplace_back(a[u][k],false);}else{I l=a[u][1]==-1?0:height[a[u][1]],r=a[u][2]==-1?0:height[a[u][2]];okay&=std::abs(l-r)<=1;height[u]=std::max(l,r)+1;}}return okay;}
#include <fstream>
#include <iostream>
#include <sstream>
struct Input {std::string data;std::istringstream input;I one(){I x;input>>x;return x;}V vector(){V a(one());for(auto&x:a)x=one();return a;}std::vector<V> matrix(int w){std::vector<V>a(one(),V(w));for(auto&r:a)for(auto&x:r)x=one();return a;}};
std::string row(const V&a){std::string s;for(I x:a){if(!s.empty())s+=' ';s+=std::to_string(x);}return s+'\n';}
int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);auto raw_input=std::string(std::istreambuf_iterator<char>(file),{});Input q{raw_input,std::istringstream(raw_input)};I n=q.one(),root=q.one();std::vector<std::array<I,3>> a(n);for(auto&r:a)for(auto&x:r)x=q.one();auto result=kernel(a,root);auto answer=std::to_string(result)+'\n';std::ofstream out(argv[2],std::ios::binary);out<<answer;std::cout<<answer.size()<<'\n';}
