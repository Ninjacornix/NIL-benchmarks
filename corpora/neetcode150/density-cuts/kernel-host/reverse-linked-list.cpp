#include <algorithm>
#include <array>
#include <cstdint>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
V kernel(std::vector<std::array<I,2>> a,I head){V out;while(head!=-1){out.push_back(a[head][0]);head=a[head][1];}std::reverse(out.begin(),out.end());return out;}
#include <fstream>
#include <iostream>
#include <sstream>
struct Input {std::string data;std::istringstream input;I one(){I x;input>>x;return x;}V vector(){V a(one());for(auto&x:a)x=one();return a;}std::vector<V> matrix(int w){std::vector<V>a(one(),V(w));for(auto&r:a)for(auto&x:r)x=one();return a;}};
std::string row(const V&a){std::string s;for(I x:a){if(!s.empty())s+=' ';s+=std::to_string(x);}return s+'\n';}
int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);auto raw_input=std::string(std::istreambuf_iterator<char>(file),{});Input q{raw_input,std::istringstream(raw_input)};I n=q.one(),head=q.one();std::vector<std::array<I,2>> a(n);for(auto &r:a){r[0]=q.one();r[1]=q.one();}auto result=kernel(a,head);auto answer=row(result);std::ofstream out(argv[2],std::ios::binary);out<<answer;std::cout<<answer.size()<<'\n';}
