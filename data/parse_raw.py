from pathlib import Path
import re,json
ls=Path('G:/IntelligentSystemDesign/data/xju_raw.txt').read_text(encoding='utf-8').splitlines(); sources={'校园新闻','通知公告','教务处通知'}; date_re=re.compile(r'^(20\d\d-\d\d-\d\d)\s+(.+)$')
start=next(i for i,l in enumerate(ls) if '完整公开信息索引' in l)
records=[]; cur=None; pending=[]; seen_url=False
for l in ls[start+1:]:
 st=l.strip()
 if not st or st.startswith('以下共') or st.startswith('日期') or '新疆工程学院公开校内信息汇总' in st: continue
 m=date_re.match(st)
 if m:
  if cur: records.append(cur)
  cur={'date':m.group(1),'category':m.group(2).strip(),'title':' '.join(pending).strip(),'source_type':'','source_page_url':'','article_url':'','summary':'','_page':None}
  pending=[]; seen_url=False; continue
 if cur is None:
  pending.append(st); continue
 if st in sources:
  cur['source_type']=st; continue
 if st.startswith('http'):
  cur['source_page_url'] += st; seen_url=True; continue
 if seen_url:
  # URL continuation lines are path/query fragments
  if re.match(r'^[\w?=&/.-]+$',st) and ('/' in st or '?' in st or st.endswith('.htm')):
   cur['source_page_url'] += st; continue
  pending.append(st)
 else:
  cur['title'] += (' ' if cur['title'] else '') + st
if cur: records.append(cur)
for r in records:
 r['title']=re.sub(r'\s+',' ',r['title']).strip(); r.pop('_page',None)
 r['tags']=[r['category']]; r['target_grades']=[]; r['target_majors']=[]; r['importance']=0.5
 r['content_type']='notice' if r['source_type']=='通知公告' else ('academic' if r['source_type']=='教务处通知' else 'news')
out=Path('G:/IntelligentSystemDesign/data/xju_records.ndjson'); out.write_text('\n'.join(json.dumps(r,ensure_ascii=False) for r in records),encoding='utf-8')
from collections import Counter
print('records',len(records),'sources',Counter(r['source_type'] for r in records),'empty_url',sum(not r['source_page_url'] for r in records),'empty_title',sum(not r['title'] for r in records))
for i in [0,1,2,28,45,134,160,170,171,281,287,290]: print(i,records[i])
