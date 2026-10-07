#include <algorithm>
#include <array>
#include <cstdint>
#include <string>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
I kernel(I k,std::string data){std::array<I,26> count{};I left=0,best=0,peak=0;for(I i=0;i<(I)(data.size());++i){peak=std::max(peak,++count[data[i]-'A']);if(i-left+1-peak>k)--count[data[left++]-'A'];best=std::max(best,i-left+1);}return best;}
#include <fstream>
#include <iostream>
#include <sstream>
struct Input {std::string data;std::istringstream input;I one(){I x;input>>x;return x;}V vector(){V a(one());for(auto&x:a)x=one();return a;}std::vector<V> matrix(int w){std::vector<V>a(one(),V(w));for(auto&r:a)for(auto&x:r)x=one();return a;}};
std::string row(const V&a){std::string s;for(I x:a){if(!s.empty())s+=' ';s+=std::to_string(x);}return s+'\n';}
int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);auto raw_input=std::string(std::istreambuf_iterator<char>(file),{});Input q{raw_input,std::istringstream(raw_input)};I k=q.one();auto start=q.data.find('\n')+1;auto data=q.data.substr(start);auto result=kernel(k,data);auto answer=std::to_string(result)+'\n';std::ofstream out(argv[2],std::ios::binary);out<<answer;std::cout<<answer.size()<<'\n';}
