"""Freeze spelling counts; no model inference or corpus rewrites."""
import json,tiktoken
samples=['!sort(a)','!find(a,10,b)','!map(&c,a)','!filter(&c,a)','!fold(&c,a,0)','b(&c,a)','!plugin(7,0,a)','!7.0(a)','!7:0(a)','!7/0(a)','!m.a(a)','!7.12(a,b)','!plugin(7,12,a,b)']
print(json.dumps({'tiktoken':tiktoken.__version__,'counts':{s:{n:len(tiktoken.get_encoding(n).encode(s)) for n in ['cl100k_base','o200k_base']} for s in samples}},indent=2))
