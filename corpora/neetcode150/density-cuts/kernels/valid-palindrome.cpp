#include <algorithm>
#include <cstdint>
#include <string>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
I kernel(std::string data){std::string a;for(unsigned char x:data){if(x>='A'&&x<='Z')x+=32;if((x>='a'&&x<='z')||(x>='0'&&x<='9'))a+=x;}auto b=a;std::reverse(b.begin(),b.end());return a==b;}
