#include <cstdint>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
V kernel(I r,I c,V a){V out;I top=0,bottom=r,left=0,right=c;while(top<bottom&&left<right){for(I j=left;j<right;++j)out.push_back(a[top*c+j]);++top;for(I i=top;i<bottom;++i)out.push_back(a[i*c+right-1]);--right;if(top<bottom){for(I j=right;j>left;--j)out.push_back(a[(bottom-1)*c+j-1]);--bottom;}if(left<right){for(I i=bottom;i>top;--i)out.push_back(a[(i-1)*c+left]);++left;}}return out;}
#include <fstream>
#include <iostream>
#include <sstream>
struct Input {std::string data;std::istringstream input;I one(){I x;input>>x;return x;}V vector(){V a(one());for(auto&x:a)x=one();return a;}std::vector<V> matrix(int w){std::vector<V>a(one(),V(w));for(auto&r:a)for(auto&x:r)x=one();return a;}};
std::string row(const V&a){std::string s;for(I x:a){if(!s.empty())s+=' ';s+=std::to_string(x);}return s+'\n';}
int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);auto raw_input=std::string(std::istreambuf_iterator<char>(file),{});Input q{raw_input,std::istringstream(raw_input)};I r=q.one(),c=q.one();V a(r*c);for(auto&x:a)x=q.one();auto result=kernel(r,c,a);auto answer=row(result);std::ofstream out(argv[2],std::ios::binary);out<<answer;std::cout<<answer.size()<<'\n';}
