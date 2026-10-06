// Original benchmark work, MIT license. Same algorithm class, not an NIL ABI.
#include <chrono>
#include <cstdio>
#include <fstream>
#include <iterator>
#include <string>
#include <string_view>
#include <unordered_map>
#include <vector>
#include <cstdint>
#include <cstdlib>
using Clock=std::chrono::steady_clock;
struct Ordered {
 struct Entry {uint64_t hash;std::string key;int64_t value;};
 std::vector<Entry> entries;std::vector<size_t> buckets=std::vector<size_t>(8);
 uint64_t probes=0,hash_bytes=0;
 static uint64_t hash(std::string_view k){uint64_t h=14695981039346656037ull;for(unsigned char c:k)h=(h^c)*1099511628211ull;return h;}
 size_t find(std::string_view k,uint64_t h){size_t slot=h&(buckets.size()-1);for(;;){
#ifdef NIL_MAP_PROFILE
++probes;
#endif
if(!buckets[slot] || (entries[buckets[slot]-1].hash==h && entries[buckets[slot]-1].key==k))return slot;slot=(slot+1)&(buckets.size()-1);}}
 void grow(){buckets.assign(buckets.size()*2,0);for(size_t i=0;i<entries.size();++i){size_t slot=entries[i].hash&(buckets.size()-1);while(buckets[slot])slot=(slot+1)&(buckets.size()-1);buckets[slot]=i+1;}}
 void put(std::string_view k,int64_t value){
#ifdef NIL_MAP_PROFILE
hash_bytes+=k.size();
#endif
uint64_t h=hash(k);size_t s=find(k,h);if(buckets[s]){entries[buckets[s]-1].value=value;return;}if(entries.size()==buckets.size()/2){grow();s=find(k,h);}entries.push_back({h,std::string(k),value});buckets[s]=entries.size();}
 int64_t get(std::string_view k){
#ifdef NIL_MAP_PROFILE
hash_bytes+=k.size();
#endif
size_t s=find(k,hash(k));return buckets[s]?entries[buckets[s]-1].value:-1;}
};
int main(int argc,char**argv){
 if(argc!=6)return 2;std::ifstream file(argv[1],std::ios::binary|std::ios::ate);if(!file)return 3;auto length=file.tellg();std::string data(static_cast<size_t>(length),0);file.seekg(0);file.read(data.data(),length);if(!file)return 3;
 size_t n=std::strtoull(argv[2],nullptr,10),w=std::strtoull(argv[3],nullptr,10);int op=std::atoi(argv[4]);bool ordered=std::string(argv[5])=="ordered";
 if(data.size()!=n*w)return 3;Ordered o;std::unordered_map<std::string,int64_t> u;
 for(size_t i=0;i<n;i++){std::string_view key(data.data()+i*w,w);if(ordered)o.put(key,i);else u.emplace(std::string(key),i);}
 int64_t result=0;
 if(op==0)result=n;
 else if(op==3){for(int pass=0;pass<3;pass++)if(ordered){for(auto &e:o.entries)result+=e.value;}else{for(auto &e:u)result+=e.second;}}
 else for(int pass=0;pass<3;pass++)for(size_t i=0;i<n;i++){
  std::string_view view(data.data()+i*w,w);std::string key(view);if(op==2)key[w-1]=char(128);
  if(op==4){if(ordered)o.put(view,i+1);else u[std::string(view)]=i+1;}
  else if(ordered){int64_t v=o.get(key);result+=op==1?v:(v<0);}
  else{auto it=u.find(key);result+=op==1?it->second:(it==u.end());}
 }
 if(op==4)result=n;
 std::printf("%lld\n",static_cast<long long>(result));

#ifdef NIL_MAP_PROFILE
 if(ordered)std::fprintf(stderr,"probes=%llu hash_bytes=%llu\n",(unsigned long long)o.probes,(unsigned long long)o.hash_bytes);
 if(ordered){uint64_t hash_sum=0;auto t=Clock::now();for(int pass=0;pass<3;pass++)for(size_t i=0;i<n;i++)hash_sum+=Ordered::hash(std::string_view(data.data()+i*w,w));auto ns=std::chrono::duration_cast<std::chrono::nanoseconds>(Clock::now()-t).count();std::fprintf(stderr,"hash_only_ns_per_key=%.3f checksum=%llu\n",double(ns)/(3*n),(unsigned long long)hash_sum);}
#endif
}
