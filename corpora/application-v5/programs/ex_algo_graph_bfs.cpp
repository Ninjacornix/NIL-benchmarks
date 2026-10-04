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
 vector<vector<long long>> rows;for(size_t i=0;i<values.size();){long long n=values[i++];rows.emplace_back(values.begin()+i,values.begin()+i+n);i+=n;}
 vector<bool> seen(rows.size());vector<long long> queue;if(!rows.empty()){queue.push_back(0);seen[0]=true;}
 for(size_t i=0;i<queue.size();i++){auto vertex=queue[i];result.push_back(vertex);for(auto next:rows[vertex])if(!seen[next]){seen[next]=true;queue.push_back(next);}}
 string output="[";for(size_t i=0;i<result.size();i++){if(i)output+=",";output+=to_string(result[i]);}output+="]";
 ofstream(output_path,ios::binary)<<output;return output.size();
}
