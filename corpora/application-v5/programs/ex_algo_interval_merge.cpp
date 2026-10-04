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
 vector<pair<long long,long long>> intervals,merged;for(size_t i=0;i<values.size();i+=2)intervals.emplace_back(values[i],values[i+1]);sort(intervals.begin(),intervals.end());
 for(auto [lo,hi]:intervals){if(merged.empty()||lo>merged.back().second)merged.emplace_back(lo,hi);else merged.back().second=max(merged.back().second,hi);}
 string output="[";for(size_t i=0;i<merged.size();i++){if(i)output+=",";output+="["+to_string(merged[i].first)+","+to_string(merged[i].second)+"]";}output+="]";
 ofstream(output_path,ios::binary)<<output;return output.size();
}
