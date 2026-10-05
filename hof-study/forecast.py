"""Preregistered spelling costs; source density is not model efficiency."""
import json
import tiktoken
SAMPLES = {
 'signature_explicit': 'fn(i):i', 'signature_parenthesized': '(i):i',
 'signature_bracketed': '[i:i]', 'reference_ampersand': '&b',
 'reference_explicit': 'fn(b)', 'reference_prefixed': 'ref(b)',
 'parameter_call_caret': '^b(a)', 'parameter_call_explicit': 'apply(b,a)',
 'module_reference': '&!plugin(1,0)',
 'named_example': '=b(&c,20)\n([i:i],i)=^a(b)\n1=a+1',
 'anonymous_candidate': '=b(fn(i):i=a+1,20)\n([i:i],i)=^a(b)',
 'explicit_state_callback': '[s,s:s]',
}
print(json.dumps({'schema':1,'tiktoken':tiktoken.__version__, 'counts':{
 key:{'source':source, **{name:len(tiktoken.get_encoding(name).encode(source)) for name in ['cl100k_base','o200k_base']}} for key,source in SAMPLES.items()}}, indent=2))
