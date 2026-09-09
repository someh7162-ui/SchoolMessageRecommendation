import pdfplumber,re,json
from pathlib import Path
pdf_path='F:/DownLoadThings/新疆工程学院公开校内信息汇总.pdf'; out_path=Path('G:/IntelligentSystemDesign/data/xju_records.ndjson')
sources={'校园新闻','通知公告','教务通知'}; date_re=re.compile(r'^20\d\d-\d\d-\d\d$')
records=[]; cur=None; pending=[]; seen_url=False
with pdfplumber.open(pdf_path) as pdf:
  for pno,page in enumerate(pdf.pages):
    if pno<3: continue
    words=page.extract_words(x_tolerance=1,y_tolerance=3,keep_blank_chars=False)
    lines=[]
    for w in sorted(words,key=lambda w:(w['top'],w['x0'])):
      if not lines or abs(w['top']-lines[-1][0])>2: lines.append([w['top'],[]])
      lines[-1][1].append(w)
    for top,ws in lines:
      texts=' '.join(w['text'] for w in ws)
      # classify line columns
      datew=next((w for w in ws if date_re.match(w['text']) and 70<=w['x0']<=150),None)
      title_words=[w['text'] for w in ws if 300<=w['x0']<480 and not w['text'].startswith('http')]
      urlw=next((w['text'] for w in ws if w['text'].startswith('http')),None)
      srcw=next((w['text'] for w in ws if w['x0']>=470 and w['text'] in sources),None)
      if datew:
        if cur: records.append(cur)
        catw=next((w for w in ws if 180<=w['x0']<300),None)
        cur={'date':datew['text'],'category':catw['text'] if catw else '', 'title':' '.join(pending+title_words).strip(), 'source_type':srcw or '', 'source_page_url':urlw or '', 'article_url':'','summary':'','_page':pno+1}
        pending=[]; seen_url=bool(urlw)
        continue
      # ignore non-data headers/footers
      if '新疆工程学院公开校内信息汇总' in texts or texts.startswith('日期') or texts.startswith('4.') or texts.startswith('以下共'):
        continue
      if cur is None:
        if title_words: pending.extend(title_words)
        continue
      if not seen_url:
        if title_words: cur['title'] += (' ' if cur['title'] else '') + ' '.join(title_words)
        if urlw: cur['source_page_url']=urlw; seen_url=True
        if srcw: cur['source_type']=srcw
      else:
        # next record's title prefix lines accumulate until date
        if title_words: pending.extend(title_words)
        if srcw and not cur['source_type']: cur['source_type']=srcw
        if urlw and not cur['source_page_url']: cur['source_page_url']=urlw
if cur: records.append(cur)
for r in records:
  r['title']=re.sub(r'\s+',' ',r['title']).strip(); r.pop('_page',None)
  r['tags']=[r['category']]; r['target_grades']=[]; r['target_majors']=[]; r['importance']=0.5
  r['content_type']='notice' if r['source_type']=='通知公告' else ('academic' if r['source_type']=='教务通知' else 'news')
out_path.write_text('\n'.join(json.dumps(r,ensure_ascii=False) for r in records),encoding='utf-8')
from collections import Counter
print('records',len(records),'sources',Counter(r['source_type'] for r in records),'empty_url',sum(not r['source_page_url'] for r in records))
for r in records[:8]: print(r)
