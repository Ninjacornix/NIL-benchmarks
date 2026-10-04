#include <fstream>
#include <string>
#include <vector>
#include <functional>
using namespace std;
long long solve(const string& input_path,const string& output_path) {
 ifstream input(input_path);string text((istreambuf_iterator<char>(input)),{});
 struct Node{string data;long long left,right;};vector<Node> nodes;
 for(size_t i=text.find('[')+1;i<text.size()&&text[i]!=']';i++)if(text[i]=='"'){
  auto end=text.find('"',i+1);string value=text.substr(i+1,end-i-1);i=end;
  if(nodes.empty()){nodes.push_back({value,-1,-1});continue;}
  long long index=0;for(;;){bool left=value<=nodes[index].data;long long child=left?nodes[index].left:nodes[index].right;
   if(child<0){if(left)nodes[index].left=nodes.size();else nodes[index].right=nodes.size();nodes.push_back({value,-1,-1});break;}index=child;}
 }
 function<string(long long)> dump=[&](long long i)->string{if(i<0)return "null";return "{\"data\":\""+nodes[i].data+"\",\"left\":"+dump(nodes[i].left)+",\"right\":"+dump(nodes[i].right)+"}";};
 auto output=dump(nodes.empty()?-1:0);ofstream(output_path,ios::binary)<<output;return output.size();
}
