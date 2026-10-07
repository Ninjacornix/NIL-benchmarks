#include <array>
#include <cstdint>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
I kernel(std::vector<std::array<I,3>> a,I root){I n=a.size();V stack;I u=root,prev=0;bool has=false;while(u!=-1||!stack.empty()){while(u!=-1){stack.push_back(u);u=a[u][1];}u=stack.back();stack.pop_back();if(has&&a[u][0]<=prev)return 0;has=true;prev=a[u][0];u=a[u][2];}return 1;}
#include <fstream>
#include <iostream>
#include <sstream>
struct Input {std::string data;std::istringstream input;I one(){I x;input>>x;return x;}V vector(){V a(one());for(auto&x:a)x=one();return a;}std::vector<V> matrix(int w){std::vector<V>a(one(),V(w));for(auto&r:a)for(auto&x:r)x=one();return a;}};
std::string row(const V&a){std::string s;for(I x:a){if(!s.empty())s+=' ';s+=std::to_string(x);}return s+'\n';}
int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);auto raw_input=std::string(std::istreambuf_iterator<char>(file),{});Input q{raw_input,std::istringstream(raw_input)};I n=q.one(),root=q.one();std::vector<std::array<I,3>> a(n);for(auto&r:a)for(auto&x:r)x=q.one();auto result=kernel(a,root);auto answer=std::to_string(result)+'\n';std::ofstream out(argv[2],std::ios::binary);out<<answer;std::cout<<answer.size()<<'\n';}
