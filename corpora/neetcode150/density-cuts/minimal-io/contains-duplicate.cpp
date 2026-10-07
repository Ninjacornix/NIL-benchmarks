#include <cstdint>
#include <unordered_set>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
I kernel(V a){ std::unordered_set<I> seen; for(I x:a) if(!seen.insert(x).second)return 1;return 0;}
#include <fstream>
#include <iostream>
#include <sstream>
struct Input {std::string data;std::istringstream input;I one(){I x;input>>x;return x;}V vector(){V a(one());for(auto&x:a)x=one();return a;}std::vector<V> matrix(int w){std::vector<V>a(one(),V(w));for(auto&r:a)for(auto&x:r)x=one();return a;}};
std::string row(const V&a){std::string s;for(I x:a){if(!s.empty())s+=' ';s+=std::to_string(x);}return s+'\n';}
int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);auto raw_input=std::string(std::istreambuf_iterator<char>(file),{});Input q{raw_input,std::istringstream(raw_input)};auto a=q.vector();auto result=kernel(a);auto answer=std::to_string(result)+'\n';std::ofstream out(argv[2],std::ios::binary);out<<answer;std::cout<<answer.size()<<'\n';}
