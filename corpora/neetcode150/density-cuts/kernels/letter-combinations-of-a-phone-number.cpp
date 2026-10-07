#include <array>
#include <cstdint>
#include <functional>
#include <string>
#include <vector>
using I=std::int64_t;
using V=std::vector<I>;
std::vector<std::string> kernel(std::string data){if(data.empty())return {};std::array<std::string,8> letters={"abc","def","ghi","jkl","mno","pqrs","tuv","wxyz"};std::vector<std::string> out;std::function<void(int,std::string)> visit=[&](int i,std::string prefix){if(i==(int)data.size()){out.push_back(prefix);return;}for(char c:letters[data[i]-'2'])visit(i+1,prefix+c);};visit(0,"");return out;}
