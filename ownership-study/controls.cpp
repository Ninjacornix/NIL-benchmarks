// Original NIL benchmark sources, licensed under the benchmark repository MIT license.
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iterator>
#include <string>
#include <vector>
int main(int argc,char **argv) {
 if(argc!=3) return 1;
 std::string op=argv[1];
 if(op=="append") {
  std::vector<unsigned char> v; size_t n=std::strtoull(argv[2],nullptr,10);
  for(size_t i=0;i<n;i++) v.push_back('x');
  std::printf("%zu\n",v.size()); return 0;
 }
 if(op=="insertion" || op=="sort") {
  size_t n=std::strtoull(argv[2],nullptr,10); std::vector<long long> v(n);
  if(op=="sort") {long long c=1;for(size_t i=0;i<n;i++) {c=(c*25173+13849)%65536;v[i]=c;}}
  else for(size_t i=0;i<n;i++) v[i]=n-i;
  if(op=="sort") std::sort(v.begin(),v.end());
  else for(size_t i=1;i<n;i++) for(size_t j=i;j>0 && v[j]<v[j-1];j--) std::swap(v[j-1],v[j]);
  std::printf("[");for(size_t i=0;i<n;i++) std::printf("%s%lld",i?",":"",v[i]);std::printf("]\n");return 0;
 }
 std::ifstream f(argv[2],std::ios::binary|std::ios::ate);if(!f) return 1;
 auto size=f.tellg();f.seekg(0);std::vector<unsigned char> in(size);f.read(reinterpret_cast<char*>(in.data()),size);if(!f) return 1;
 std::vector<unsigned char> out;
 if(op=="filter") std::copy_if(in.begin(),in.end(),std::back_inserter(out),[](unsigned char c){return c%2==0;});
 else if(op=="map") {out.resize(in.size());std::transform(in.begin(),in.end(),out.begin(),[](unsigned char c){return 255-c;});}
 else return 1;
 std::fwrite(out.data(),1,out.size(),stdout);std::putchar('\n');return 0;
}
