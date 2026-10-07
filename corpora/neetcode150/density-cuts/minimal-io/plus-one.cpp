#include <cstdint>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
V kernel(V a){I carry=1;for(I i=(I)a.size()-1;i>=0;--i){I x=a[i]+carry;a[i]=x%10;carry=x/10;}if(carry)a.insert(a.begin(),1);return a;}
#include <fstream>
#include <iostream>
#include <sstream>
struct Input {std::string data;std::istringstream input;I one(){I x;input>>x;return x;}V vector(){V a(one());for(auto&x:a)x=one();return a;}std::vector<V> matrix(int w){std::vector<V>a(one(),V(w));for(auto&r:a)for(auto&x:r)x=one();return a;}};
std::string row(const V&a){std::string s;for(I x:a){if(!s.empty())s+=' ';s+=std::to_string(x);}return s+'\n';}
int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);auto raw_input=std::string(std::istreambuf_iterator<char>(file),{});Input q{raw_input,std::istringstream(raw_input)};auto a=q.vector();auto result=kernel(a);auto answer=row(result);std::ofstream out(argv[2],std::ios::binary);out<<answer;std::cout<<answer.size()<<'\n';}
