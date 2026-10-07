#include <cstdint>
#include <functional>
#include <string>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
std::vector<std::string> kernel(I n){std::vector<std::string> out;std::function<void(std::string,int,int)> visit=[&](std::string s,int a,int b){if(b==n){out.push_back(s);return;}if(a<n)visit(s+'(',a+1,b);if(b<a)visit(s+')',a,b+1);};visit("",0,0);return out;}
