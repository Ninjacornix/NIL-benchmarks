#include <algorithm>
#include <cstdint>
#include <stdexcept>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
I kernel(V a,V b){if(a.size()>b.size())std::swap(a,b);I lo=0,hi=a.size(),half=(a.size()+b.size()+1)/2;const I inf=INT64_MAX;while(lo<=hi){I i=(lo+hi)/2,j=half-i,al=i?a[i-1]:-inf,ar=i<(I)a.size()?a[i]:inf,bl=j?b[j-1]:-inf,br=j<(I)b.size()?b[j]:inf;if(al>br)hi=i-1;else if(bl>ar)lo=i+1;else return (a.size()+b.size())%2?2*std::max(al,bl):std::max(al,bl)+std::min(ar,br);}throw std::runtime_error("partition");}
#include <fstream>
#include <iostream>
#include <sstream>
struct Input {std::string data;std::istringstream input;I one(){I x;input>>x;return x;}V vector(){V a(one());for(auto&x:a)x=one();return a;}std::vector<V> matrix(int w){std::vector<V>a(one(),V(w));for(auto&r:a)for(auto&x:r)x=one();return a;}};
std::string row(const V&a){std::string s;for(I x:a){if(!s.empty())s+=' ';s+=std::to_string(x);}return s+'\n';}
int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);auto raw_input=std::string(std::istreambuf_iterator<char>(file),{});Input q{raw_input,std::istringstream(raw_input)};auto a=q.vector(),b=q.vector();auto result=kernel(a,b);auto answer=std::to_string(result)+'\n';std::ofstream out(argv[2],std::ios::binary);out<<answer;std::cout<<answer.size()<<'\n';}
