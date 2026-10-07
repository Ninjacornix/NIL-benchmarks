#include <cstdint>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
I kernel(V a,I target){I lo=0,hi=(I)a.size()-1;while(lo<=hi){I m=(lo+hi)/2;if(a[m]==target)return m;if(a[lo]<=a[m]){if(a[lo]<=target&&target<a[m])hi=m-1;else lo=m+1;}else{if(a[m]<target&&target<=a[hi])lo=m+1;else hi=m-1;}}return -1;}
#include <fstream>
#include <iostream>
#include <sstream>
struct Input {std::string data;std::istringstream input;I one(){I x;input>>x;return x;}V vector(){V a(one());for(auto&x:a)x=one();return a;}std::vector<V> matrix(int w){std::vector<V>a(one(),V(w));for(auto&r:a)for(auto&x:r)x=one();return a;}};
std::string row(const V&a){std::string s;for(I x:a){if(!s.empty())s+=' ';s+=std::to_string(x);}return s+'\n';}
int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);auto raw_input=std::string(std::istreambuf_iterator<char>(file),{});Input q{raw_input,std::istringstream(raw_input)};auto a=q.vector();I target=q.one();auto result=kernel(a,target);auto answer=std::to_string(result)+'\n';std::ofstream out(argv[2],std::ios::binary);out<<answer;std::cout<<answer.size()<<'\n';}
