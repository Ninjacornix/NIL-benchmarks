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
 for(long long i=values.empty()?-1:0;i!=-1;i=values[2*i+1])result.push_back(values[2*i]);
 string output="[";for(size_t i=0;i<result.size();i++){if(i)output+=",";output+=to_string(result[i]);}output+="]";
 ofstream(output_path,ios::binary)<<output;return output.size();
}
