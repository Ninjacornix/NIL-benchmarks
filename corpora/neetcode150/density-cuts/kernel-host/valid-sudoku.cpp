#include <array>
#include <cstdint>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
I kernel(V a){std::array<int,9> rs{},cs{},bs{};for(int i=0;i<81;++i){int x=a[i];if(!x)continue;int b=(i/27)*3+(i%9)/3,bit=1<<x;if((rs[i/9]|cs[i%9]|bs[b])&bit)return 0;rs[i/9]|=bit;cs[i%9]|=bit;bs[b]|=bit;}return 1;}
#include <fstream>
#include <iostream>
#include <sstream>
struct Input {std::string data;std::istringstream input;I one(){I x;input>>x;return x;}V vector(){V a(one());for(auto&x:a)x=one();return a;}std::vector<V> matrix(int w){std::vector<V>a(one(),V(w));for(auto&r:a)for(auto&x:r)x=one();return a;}};
std::string row(const V&a){std::string s;for(I x:a){if(!s.empty())s+=' ';s+=std::to_string(x);}return s+'\n';}
int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);auto raw_input=std::string(std::istreambuf_iterator<char>(file),{});Input q{raw_input,std::istringstream(raw_input)};V a(81);for(auto&x:a)x=q.one();auto result=kernel(a);auto answer=std::to_string(result)+'\n';std::ofstream out(argv[2],std::ios::binary);out<<answer;std::cout<<answer.size()<<'\n';}
