#include <algorithm>
#include <fstream>
#include <functional>
#include <sstream>
#include <string>
#include <vector>
using namespace std;
long long solve(const string& input_path,const string& output_path) {
 ifstream input(input_path); string text((istreambuf_iterator<char>(input)),{});
 replace(text.begin(),text.end(),',',' '); istringstream parser(text);
 vector<long long> values,result;long long value;while(parser>>value)values.push_back(value);
 struct Node {long long value,left,right;};vector<Node> nodes;
 for(auto value:values){if(nodes.empty()){nodes.push_back({value,-1,-1});continue;}
  long long index=0;for(;;){bool left=value<=nodes[index].value;long long child=left?nodes[index].left:nodes[index].right;
   if(child<0){if(left)nodes[index].left=nodes.size();else nodes[index].right=nodes.size();nodes.push_back({value,-1,-1});break;}index=child;}}
 function<void(long long)> visit=[&](long long i){if(i<0)return;visit(nodes[i].left);result.push_back(nodes[i].value);visit(nodes[i].right);};if(!nodes.empty())visit(0);
 string output="[";for(size_t i=0;i<result.size();i++){if(i)output+=",";output+=to_string(result[i]);}output+="]";
 ofstream(output_path,ios::binary)<<output;return output.size();
}
