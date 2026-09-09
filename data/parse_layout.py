from pathlib import Path
import re,json
text=Path('G:/IntelligentSystemDesign/data/xju_text.txt').read_text(encoding='utf-8'); ls=text.splitlines();
sources={'校园新闻','通知公告','教务处通知'}; date_re=re.compile(r'^20\d\d-\d\d-\d\d$')
start=next(i for i,l in enumerate(ls) if '完整公开信息索引' in l)
records=[]; cur=None; pending=[]; seen_url=False
for l in ls[start+1:]:
  st=l.strip()
  if not st or '新疆工程学院公开校内信息汇总' in l or st.startswith('日期') or st.startswith('以下共'): continue
  # detect date row via first field after strip
  parts=re.split(r'\s{2,}', st)
  date=None
  if parts and date_re.match(parts[0]): date=parts[0]
  if date:
    if cur: records.append(cur)
    cat=parts[1] if len(parts)>1 else ''
    src=next((x for x in parts[1:] if x in sources),'')
    title_parts=[x for x in parts[2:] if x not in sources]
    title=' '.join(pending+title_parts).strip(); pending=[]
    cur={'date':date,'category':cat,'title':title,'source_type':src,'source_page_url':'','article_url':'','summary':'','_page':None}; seen_url=False
    continue
  if cur is None:
    if st.startswith('http') or st in sources: continue
    pending.append(st); continue
  # URLs and URL continuation
  if st.startswith('http'):
    cur['source_page_url'] += st; seen_url=True; continue
  if seen_url and (re.match(r'^[\w?=&/.-]+$',st) or st.endswith('.htm')) and not any(c in st for c in '，。；：'): 
    cur['source_page_url'] += st; continue
  if st in sources:
    cur['source_type']=st; continue
  # before URL: title continuation; after URL: next row title prefix
  if not seen_url:
    # remove source token at line end if any
    cur['title'] += (' ' if cur['title'] else '') + st
  else:
    pending.append(st)
if cur: records.append(cur)
for r in records:
  r['title']=re.sub(r'\s+',' ',r['title']).strip(); r.pop('_page',None)
  r['tags']=[r['category']]; r['target_grades']=[]; r['target_majors']=[]; r['importance']=0.5
  r['content_type']='notice' if r['source_type']=='通知公告' else ('academic' if r['source_type']=='教务处通知' else 'news')
out=Path('G:/IntelligentSystemDesign/data/xju_records.ndjson'); out.write_text('\n'.join(json.dumps(r,ensure_ascii=False) for r in records),encoding='utf-8')
from collections import Counter
print('records',len(records),'sources',Counter(r['source_type'] for r in records),'empty_url',sum(not r['source_page_url'] for r in records),'empty_title',sum(not r['title'] for r in records))
for r in records[:3]+[records[134],records[-1]]: print(r)
