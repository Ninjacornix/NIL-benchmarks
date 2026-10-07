#include <cstdint>
#include <functional>
#include <string>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
std::vector<std::string> kernel(I n){std::vector<std::string> out;std::function<void(std::string,int,int)> visit=[&](std::string s,int a,int b){if(b==n){out.push_back(s);return;}if(a<n)visit(s+'(',a+1,b);if(b<a)visit(s+')',a,b+1);};visit("",0,0);return out;}
#include <fstream>
#include <iostream>
#include <sstream>
struct Input {std::string data;std::istringstream input;I one(){I x;input>>x;return x;}V vector(){V a(one());for(auto&x:a)x=one();return a;}std::vector<V> matrix(int w){std::vector<V>a(one(),V(w));for(auto&r:a)for(auto&x:r)x=one();return a;}};
std::string row(const V&a){std::string s;for(I x:a){if(!s.empty())s+=' ';s+=std::to_string(x);}return s+'\n';}
int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);auto raw_input=std::string(std::istreambuf_iterator<char>(file),{});Input q{raw_input,std::istringstream(raw_input)};I n=q.one();auto result=kernel(n);auto answer=[&]{std::string s;for(auto&r:result)s+=r+'\n';return s;}();std::ofstream out(argv[2],std::ios::binary);out<<answer;std::cout<<answer.size()<<'\n';}
