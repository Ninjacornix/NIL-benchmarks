#include <charconv>
#include <cstdint>
#include <fstream>
#include <functional>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
using I = std::int64_t;
using V = std::vector<I>;
struct Input {
 std::string data; std::size_t cursor=0;
 I one() { while(cursor<data.size() && data[cursor]<=32) ++cursor; I x=0;
 auto result=std::from_chars(data.data()+cursor,data.data()+data.size(),x);
 if(result.ec!=std::errc()) throw std::runtime_error("bad fixture"); cursor=result.ptr-data.data(); return x; }
};
std::string scalar(I x) {return std::to_string(x)+"\n";}
std::string solve(Input &q){std::istringstream in(q.data);int r,c;in>>r>>c;std::vector<std::string>board(r);for(auto&x:board)in>>x;std::string word;in>>word;std::vector<bool>seen(r*c);std::function<bool(int,int,int)>visit=[&](int i,int j,int k){if(k==(int)word.size())return true;if(i<0||j<0||i>=r||j>=c||seen[i*c+j]||board[i][j]!=word[k])return false;seen[i*c+j]=true;bool yes=visit(i+1,j,k+1)||visit(i-1,j,k+1)||visit(i,j+1,k+1)||visit(i,j-1,k+1);seen[i*c+j]=false;return yes;};for(int i=0;i<r;++i)for(int j=0;j<c;++j)if(visit(i,j,0))return scalar(1);return scalar(word.empty());}

int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);Input q{std::string(std::istreambuf_iterator<char>(file),{})};auto answer=solve(q);std::ofstream out(argv[2],std::ios::binary);out.write(answer.data(),answer.size());std::cout<<answer.size()<<'\n';}
