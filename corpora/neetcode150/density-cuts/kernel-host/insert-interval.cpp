#include <algorithm>
#include <cstdint>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
std::vector<V> kernel(std::vector<V> a,I lo,I hi){std::vector<V> out;bool inserted=false;for(auto r:a){if(r[1]<lo)out.push_back(r);else if(r[0]>hi){if(!inserted){out.push_back({lo,hi});inserted=true;}out.push_back(r);}else{lo=std::min(lo,r[0]);hi=std::max(hi,r[1]);}}if(!inserted)out.push_back({lo,hi});return out;}
#include <fstream>
#include <iostream>
#include <sstream>
struct Input {std::string data;std::istringstream input;I one(){I x;input>>x;return x;}V vector(){V a(one());for(auto&x:a)x=one();return a;}std::vector<V> matrix(int w){std::vector<V>a(one(),V(w));for(auto&r:a)for(auto&x:r)x=one();return a;}};
std::string row(const V&a){std::string s;for(I x:a){if(!s.empty())s+=' ';s+=std::to_string(x);}return s+'\n';}
int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);auto raw_input=std::string(std::istreambuf_iterator<char>(file),{});Input q{raw_input,std::istringstream(raw_input)};auto a=q.matrix(2);I lo=q.one(),hi=q.one();auto result=kernel(a,lo,hi);auto answer=[&]{std::string s;for(auto&r:result)s+=row(r);return s;}();std::ofstream out(argv[2],std::ios::binary);out<<answer;std::cout<<answer.size()<<'\n';}
