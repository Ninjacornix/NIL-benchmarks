#include <algorithm>
#include <cstdint>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
std::vector<V> kernel(V a){std::sort(a.begin(),a.end());std::vector<V> out;for(int i=0;i+2<(int)a.size();++i){if(i&&a[i]==a[i-1])continue;int l=i+1,r=a.size()-1;while(l<r){I s=a[i]+a[l]+a[r];if(s<0)++l;else if(s>0)--r;else{out.push_back({a[i],a[l],a[r]});++l;--r;while(l<r&&a[l]==a[l-1])++l;while(l<r&&a[r]==a[r+1])--r;}}}return out;}
#include <fstream>
#include <iostream>
#include <sstream>
struct Input {std::string data;std::istringstream input;I one(){I x;input>>x;return x;}V vector(){V a(one());for(auto&x:a)x=one();return a;}std::vector<V> matrix(int w){std::vector<V>a(one(),V(w));for(auto&r:a)for(auto&x:r)x=one();return a;}};
std::string row(const V&a){std::string s;for(I x:a){if(!s.empty())s+=' ';s+=std::to_string(x);}return s+'\n';}
int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);auto raw_input=std::string(std::istreambuf_iterator<char>(file),{});Input q{raw_input,std::istringstream(raw_input)};auto a=q.vector();auto result=kernel(a);auto answer=[&]{std::string s;for(auto&r:result)s+=row(r);return s;}();std::ofstream out(argv[2],std::ios::binary);out<<answer;std::cout<<answer.size()<<'\n';}
