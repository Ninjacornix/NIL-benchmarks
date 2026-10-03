"""Reproduce frozen byte adapters and upstream expected-value fixtures.

MIT: derived from Exercism canonical data; see EXERCISM_LICENSE.
No reference-solution algorithm is used to determine expected output.
Run explicitly; do not import this authoring utility.
"""
from pathlib import Path
import json
H=Path(__file__).resolve().parent.parent;selection=json.loads((H/'external/selection.json').read_text())
blocked={
'armstrong-numbers':('integer_width','Upstream canonical property includes 108-bit and 127-bit Armstrong inputs, outside i64 parsing/arithmetic. Kept all such cases. Hand-rolled arbitrary-precision arithmetic is possible but not implemented.'),
'accumulate':('higher_order','The upstream collection/operator contract requires typed operation values and heterogeneous collections; neither is available in v5.'),
'alphametics':('maps_records','The upstream result is a dynamically keyed assignment map/null. This corpus does not implement a hand-encoded mapping/search adapter; records/maps are absent. Algorithmic emulation is possible, not proven impossible.'),
'anagram':('unicode','Unicode case-insensitive character comparison is required; no Unicode case database/operations are available. ASCII-only restriction would remove upstream cases.'),
'bank-account':('concurrency','The published banking contract requires concurrent access to shared mutable account state; v5 has no threads/synchronization/shared-state ABI.'),
'binary-search-tree':('recursive_values','The data property returns a recursive typed tree. Native recursive aggregate values are absent; a bespoke serialized-tree adapter is not implemented. This is an adapter gap, not a computability claim.'),
'bob':('unicode','General Unicode letter/case/whitespace classification lacks standard Unicode operations/data; ASCII-only approximations are not claimed correct.'),
'camicia':('nested_collections','Game cycle detection needs a set of variable-length deck states. No nested sequence/set representation; hand-encoded state simulation is not implemented. Emulation is possible.'),
'complex-numbers':('floats','The real-part property accepts real-number complex components; v5 has no float type or parsing/formatting contract.'),
'darts':('floats','Real Cartesian coordinates and squared-radius comparisons require floating-point semantics; integer-only restriction would remove upstream cases.'),
'diffie-hellman':('entropy','The selected privateKeyIsInRange property generates a random private key; v5 Host has no randomness capability. Supplying a fixed key would change the task.'),
'dot-dsl':('maps_records','The selected parse property returns graph/node/edge attribute maps; no typed maps/records or reusable parser adapter. Serialized emulation is possible but not implemented.'),
'etl':('maps_records','Dynamic old/new score maps need a mapping adapter; no typed maps/records. Byte-encoded emulation is possible but not implemented.'),
'forth':('dynamic_dictionary','Definitions and case-insensitive words require a runtime dictionary/code representation. A bespoke dictionary/interpreter is not implemented; this is a library/adapter gap, not theoretical impossibility.'),
'gigasecond':('calendar','No date/time parsing/calendar arithmetic operation; a hand-written Gregorian adapter is not implemented. Integer/byte emulation is possible.'),
'go-counting':('maps_records','Region result has an owner and collection of coordinate pairs. No typed multi-result/record representation; a serialized flood-fill adapter is not implemented. Emulation is possible.'),
'grains':('integer_width','Square 64 yields 2^63, outside signed i64. No unsigned64/big-integer arithmetic/formatting. Hand-rolled decimal arithmetic could emulate it but is not implemented.'),
'grep':('multi_file_fixture','Upstream multi-file flags/fixtures require a multi-file Host/runner contract; the current reusable corpus harness provisions a single input file. A packed emulation would change the I/O contract.'),
'hangman':('reactive','Published task explicitly requires functional reactive programming/library integration. No first-class signals/events or integration ABI; a sequential transcript would not verify that requirement.')}

def flatten(cs):
 for c in cs:
  if 'cases' in c:yield from flatten(c['cases'])
  else:yield c

def nums(xs):return ','.join(map(str,xs))
def encode(slug,v):
 if slug in blocked and slug != 'armstrong-numbers':return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
 if slug=='acronym':s=v['phrase']
 elif slug=='affine-cipher':s=nums([v['key']['a'],v['key']['b']])+'\n'+v['phrase']
 elif slug=='all-your-base':s=nums([v['inputBase'],v['outputBase']])+'\n'+nums(v['digits'])
 elif slug=='allergies':s=str(v['score'])+'\n'+v['item']
 elif slug=='armstrong-numbers':s=str(v['number'])
 elif slug=='atbash-cipher':s=v['phrase']
 elif slug=='baffling-birthdays':s='\n'.join(v['birthdates'])
 elif slug in ['beer-song','bottle-song']:s=nums([v['startBottles'],v['takeDown']])
 elif slug=='binary':s=v['binary']
 elif slug=='binary-search':s=str(v['value'])+'\n'+nums(v['array'])
 elif slug=='book-store':s=nums(v['basket'])
 elif slug=='bowling':s=nums(v['previousRolls'])
 elif slug=='change':s=str(v['target'])+'\n'+nums(v['coins'])
 elif slug=='circular-buffer':
  codes={'read':0,'write':1,'overwrite':2,'clear':3};s=str(v['capacity'])+'\n'+'\n'.join(nums([codes[o['operation']],o.get('item',0)]) for o in v['operations'])
 elif slug=='clock':s=nums([v['hour'],v['minute']])
 elif slug=='collatz-conjecture':s=str(v['number'])
 elif slug=='connect':s='\n'.join(v['board'])
 elif slug=='crypto-square':s=v['plaintext']
 elif slug=='custom-set':s=nums(v['set'])
 elif slug=='diamond':s=v['letter']
 elif slug=='difference-of-squares':s=str(v['number'])
 elif slug=='dnd-character':s=str(v['score'])
 elif slug=='dominoes':s='\n'.join(nums(p) for p in v['dominoes'])
 elif slug=='eliuds-eggs':s=str(v['number'])
 elif slug=='flatten-array':s=json.dumps(v['array'],separators=(',',':'))
 elif slug=='flower-field':s='\n'.join(v['garden'])+ ('\n' if v['garden'] else '')
 elif slug=='food-chain':s=nums([v['startVerse'],v['endVerse']])
 elif slug=='game-of-life':s='\n'.join(''.join(map(str,row)) for row in v['matrix'])+ ('\n' if v['matrix'] else '')
 elif slug=='grade-school':s='\n'.join(str(g)+'\t'+name for name,g in v['students'])
 elif slug=='hamming':s=v['strand1']+'\n'+v['strand2']
 elif slug=='hello-world':s=''
 else:raise ValueError(slug)
 return s.encode('utf8')

def output(slug,c):
 x=c['expected']
 if isinstance(x,dict) and 'error' in x:return b'error\n'
 if slug=='circular-buffer':
  return ''.join((str(o.get('expected','ok')) if o.get('should_succeed',True) else 'error')+'\n' for o in c['input']['operations']).encode()
 if isinstance(x,bool):return b'true\n' if x else b'false\n'
 if isinstance(x,int):return f'{x}\n'.encode()
 if isinstance(x,str):return x.encode()
 if isinstance(x,list):
  if slug=='game-of-life':return ''.join(''.join(map(str,row))+'\n' for row in x).encode()
  return (''.join(str(i)+'\n' for i in x)).encode()
 return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
contracts={
'acronym':'UTF-8 phrase containing ASCII letters and separators as in the source; output acronym, hyphen/whitespace separate words, other punctuation removed.',
'affine-cipher':'Encode only (first declared property). First line a,b (integers), remaining bytes ASCII phrase. Output lowercase alphanumerics in groups of five; noncoprime key gives error\\n.',
'all-your-base':'First line inputBase,outputBase; remaining comma-separated integer digits, possibly empty. Return rebased digits one per LF; invalid base/digit gives error\\n. Values must fit signed i64.',
'allergies':'allergicTo only (first property). Score then LF then allergen name. Output true\\n or false\\n. Ignore bits above 255.',
'armstrong-numbers':'Determine whether a nonnegative integer is an Armstrong number, including the upstream 108-bit and 127-bit canonical cases; output true\\n or false\\n.',
'atbash-cipher':'Encode only. ASCII phrase becomes reversed-alphabet lowercase alphanumerics, grouped in fives; discard nonalphanumerics.',
'baffling-birthdays':'sharedBirthday only (first property): LF-separated ISO Gregorian dates. True if any two share month/day, ignoring year. Empty list is empty file.',
'beer-song':'recite: startBottles,takeDown. Return upstream verse lines with LF after each line; blank verse separators preserved.',
'binary':'decimal: ASCII binary input; invalid digit returns null (exact bytes, no LF). Signed-i64 result domain. Output decimal followed by LF.',
'binary-search':'find: target on first line, sorted unique comma-separated integer array on remaining line. Return zero-based index followed by LF; absent gives error\\n.',
'book-store':'total: comma-separated volume IDs 1..5, empty basket allowed. Price 800 cents; discounts for distinct groups 2..5 are 5/10/20/25 percent; minimize total; decimal cents plus LF.',
'bottle-song':'recite: startBottles,takeDown (1..10). Output English-count green-bottle verses, LF after each line and blank separators.',
'bowling':'score only: comma-separated rolls. Score completed ten-frame game or error\\n for invalid/incomplete rolls. Preserve strike/spare/tenth-frame bonus rules.',
'change':'findFewestCoins: target on first line, positive ascending distinct coins comma-separated on remaining line. Minimum coin count; output ascending coins each followed by LF; impossible/negative target gives error\\n.',
'circular-buffer':'run: capacity first line; then opcode,item rows (read=0/write=1/overwrite=2/clear=3). For each op emit read value, ok or error followed by LF. Match full/empty and overwrite FIFO semantics.',
'clock':'create only: hour,minute integers. Normalize modulo one day, output HH:MM, no LF.',
'collatz-conjecture':'steps: positive canonical i64. Output step count with LF; nonpositive gives error\\n. Domain requires intermediates and steps within runtime limits.',
'connect':'winner: LF-separated Hex rows with indentation spaces; strip spaces. Output X, O or empty bytes. Rectangular boards; X left-right, O top-bottom.',
'crypto-square':'ciphertext: English ASCII phrase. Lowercase alphanumerics form minimum enclosing rectangle; read columns with trailing padding, separate groups by space.',
'custom-set':'empty only (first property): comma-separated integer set. Output true\\n iff empty. Other set API methods are explicitly outside this adapted task.',
'diamond':'rows: single uppercase A..Z. Output symmetric square of letters/spaces with LF after each row.',
'difference-of-squares':'squareOfSum only (first property): nonnegative i64 N within arithmetic bounds. Output square of sum 1..N with LF.',
'dnd-character':'modifier only (first property): score 3..18. Output floor((score-10)/2) with LF. Random ability generation is not included in this property.',
'dominoes':'canChain: LF-separated nonnegative integer pairs x,y. Output true\\n iff all tiles can form a closed chain (empty allowed).',
'eliuds-eggs':'eggCount: nonnegative i64 input. Output population count with LF; no bitwise primitive assumed.',
'flatten-array':'flatten: JSON nested arrays of i64 integers and null only. Discard null and return integers in traversal order, each with LF. Strings/objects are outside source canonical domain.',
'flower-field':'annotate: rectangular LF-terminated rows of spaces/stars, empty file means no rows. Replace nonstars by neighboring star count (zero stays space); LF after each row.',
'food-chain':'recite: startVerse,endVerse in 1..8. Return source cumulative song lines, LF after each, blank verse separators.',
'game-of-life':'tick: rectangular LF-terminated ASCII 0/1 rows. One finite-board generation with dead exterior; LF after each output row.',
'grade-school':'roster only (first property): LF-separated grade TAB name records (ASCII names, positive grades). Ignore repeated names after first accepted enrollment. Output roster sorted by grade then name, each name with LF.',
'hamming':'distance: first strand then LF then second. Equal-length DNA strings. Return mismatched positions with LF; unequal length gives error\\n.',
'hello-world':'hello: input ignored. Output exactly Hello, World! with no LF.'}
tasks=[];goldens={};cases={}
for r in selection['records']:
 slug=r['slug'];raw=json.loads((H/'external'/f'{slug}.json').read_text());fs=list(flatten(raw['cases']));prop=fs[0]['property'];superseded={c['reimplements'] for c in fs if 'reimplements' in c};chosen=[c for c in fs if c['property']==prop and c['uuid'] not in superseded];fixtures=[]
 for c in chosen:
  data=encode(slug,c['input']);answer=output(slug,c);key=data.hex()
  if key in cases.get(r['id'],{}) and cases[r['id']][key]['output']!=answer.hex():raise ValueError((slug,c))
  cases.setdefault(r['id'],{})[key]={'output':answer.hex(),'canonical_uuid':c['uuid']};fixtures.append(key)
 unique=list(dict.fromkeys(fixtures));g=unique[-1];inputs=unique[:-1] or [unique[0]]
 reason=blocked.get(slug)
 task={'id':r['id'],'category':'external exercise','origin':'external','license':'MIT','provenance':{k:r[k] for k in ['source','canonical_sha256','copyright']},'source_slug':slug,'selected_property':prop,'prompt':contracts.get(slug,f"Upstream {slug} {prop} property; JSON input/output according to pinned canonical cases. No reduced substitute is claimed."),'rationale':'Mechanically selected in the first 50 alphabetical canonical-data exercises; not selected by support or token count.','inputs':inputs,'nil_status':'unsupported' if reason else 'supported','adaptation_overlap':False,'canonical_fixture_count':len(unique)}
 if reason:task.update(unsupported_reason=reason[1],missing_capabilities=[reason[0]],baseline_status='unsupported')
 tasks.append(task);goldens[r['id']]={'input':g,'output':cases[r['id']][g]['output'],'environment':{},'canonical_uuid':cases[r['id']][g]['canonical_uuid']}
(H/'external/tasks.json').write_text(json.dumps({'schema':1,'license':'MIT','scope':'First declared property per selected exercise; full matching canonical property cases, with disclosed text transport and bounded arithmetic domain. Not complete upstream exercise API.','tasks':tasks},indent=2)+'\n')
(H/'external/goldens.json').write_text(json.dumps(goldens,indent=2)+'\n');(H/'external/answers.json').write_text(json.dumps(cases,indent=2)+'\n')
print('External adaptations frozen:',len(tasks),'supported',sum(t['nil_status']=='supported' for t in tasks),'unsupported',len(blocked))
