#!/usr/bin/env python3
"""Generate the handbook's four reading editions from six chapters and four appendices."""
from pathlib import Path
import argparse, hashlib, html, json, re
from urllib.parse import urlsplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether, NextPageTemplate, Image
from reportlab.platypus.tableofcontents import TableOfContents
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
META=json.loads((ROOT/'project.json').read_text())
FRONT=ROOT/'docs/免责声明与阅读说明.md'
INTRO=ROOT/'docs/阅读路径与行动建议.md'
DOCS=['附录A-进阶原理.md','附录B-练习与模板.md','附录C-文章播客与视频.md','附录D-研究与官方资料.md','版权与使用说明.md']
LINK=re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

def sources():
    chapters=[]
    expected_counts=[4,5,5,5,5,5]
    paths=sorted((ROOT/'book').glob('*.md'))
    if len(paths)!=6:raise ValueError('Active book/ must contain exactly six chapters')
    for i,path in enumerate(paths,1):
        text=path.read_text();title=re.search(r'^# (.+)',text,re.M)[1]
        matches=list(re.finditer(r'^<a id="entry-(\d+\.\d+)"></a>\s*\n## \1 (.+)\n',text,re.M))
        entries=[]
        for j,m in enumerate(matches):
            body=text[m.end():matches[j+1].start() if j+1<len(matches) else len(text)].strip()
            entries.append({'id':m[1],'title':m[2],'body':body,'chapter':i})
        expected=[f'{i}.{j}' for j in range(1,expected_counts[i-1]+1)]
        if [e['id'] for e in entries]!=expected:raise ValueError(f'{path.name}: expected {expected}')
        lead=text[:matches[0].start()].split('# '+title,1)[1].strip()
        chapters.append({'id':i,'title':title,'entries':entries,'path':path,'lead':lead})
    return chapters
CHAPTERS=sources()
ENTRIES=[e for c in CHAPTERS for e in c['entries']]
PATHS={c['path'].relative_to(ROOT).as_posix():f'#chapter-{c["id"]}' for c in CHAPTERS}
PATHS.update({'README.md':'#about',FRONT.relative_to(ROOT).as_posix():'#disclaimer',INTRO.relative_to(ROOT).as_posix():'#reading-path'})
for i,n in enumerate(DOCS):PATHS['docs/'+n]='#appendix-'+chr(97+i) if i<4 else '#copyright'

def href(url,base):
    if urlsplit(url).scheme:return url
    if url.startswith('#'):return url
    file,sep,anchor=url.partition('#')
    target=(base/file).resolve()
    key=target.relative_to(ROOT).as_posix()
    if key in PATHS:return '#'+anchor if anchor else PATHS[key]
    return key+(sep+anchor if sep else '')

def inline(text,base=ROOT,pdf=False):
    output=[];last=0
    for m in LINK.finditer(text):
        output.append(html.escape(text[last:m.start()]));label,url=m.groups();dest=href(url,base)
        if not pdf:output.append(f'<a href="{html.escape(dest,quote=True)}">{html.escape(label)}</a>')
        elif dest.startswith(('https://','http://','#')):output.append(f'<link href="{html.escape(dest,quote=True)}" color="#235E67">{html.escape(label)}</link>')
        else:output.append(html.escape(label))
        last=m.end()
    output.append(html.escape(text[last:]));out=''.join(output)
    out=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',out)
    return re.sub(r'`([^`]+)`',r'\1' if pdf else r'<code>\1</code>',out)

def blocks(text):
    lines=text.splitlines();i=0
    while i<len(lines):
        line=lines[i].strip()
        if not line or line.startswith(('[←','<!--')):i+=1;continue
        if line.startswith('<a id='):
            yield 'anchor',re.search(r'id="([^"]+)"',line)[1];i+=1;continue
        if line.startswith('```'):
            chunk=[];i+=1
            while i<len(lines) and not lines[i].startswith('```'):chunk.append(lines[i]);i+=1
            yield 'code','\n'.join(chunk);i+=1;continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                cells=[x.strip() for x in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?',x.replace(' ','')) for x in cells):rows.append(cells)
                i+=1
            yield 'table',rows;continue
        heading=re.match(r'^(#{1,3}) (.+)',line)
        if heading:yield 'h'+str(len(heading[1])),heading[2];i+=1;continue
        if line.startswith('- '):yield 'li',line[2:];i+=1;continue
        if line.startswith('> '):yield 'quote',line[2:];i+=1;continue
        para=[line];i+=1
        while i<len(lines) and lines[i].strip() and not re.match(r'^(#|\||-|>|<a|```)',lines[i].strip()):para.append(lines[i].strip());i+=1
        yield 'p',' '.join(para)

def render_md(text,base,entry=False,document=False):
    out=[]
    for kind,v in blocks(text):
        if kind=='anchor':out.append(f'<a id="{v}"></a>')
        elif kind=='table':
            out.append('<div class="table-scroll"><table>')
            for i,row in enumerate(v):
                tag='th' if i==0 else 'td';out.append('<tr>'+''.join(f'<{tag}>{inline(cell,base)}</{tag}>' for cell in row)+'</tr>')
            out.append('</table></div>')
        elif kind=='code':out.append('<pre>'+html.escape(v)+'</pre>')
        elif kind=='li':out.append('<p class="bullet">'+inline(v,base)+'</p>')
        elif kind=='quote':out.append('<blockquote>'+inline(v,base)+'</blockquote>')
        else:
            tag=('h'+str(int(kind[1])+1) if document and kind.startswith('h') else
                 'h4' if entry and kind=='h3' else kind if kind.startswith('h') else 'p')
            cl=' class="evidence"' if v.startswith('**依据与范围：**') else ''
            out.append(f'<{tag}{cl}>{inline(v,base)}</{tag}>')
    return '\n'.join(out)

CSS='''
:root{--ink:#1c2b36;--muted:#5a6a71;--teal:#235e67;--paper:#faf8f3;--line:#dddeda}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:var(--anchor-offset,125px)}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.85 -apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}a{color:var(--teal);text-underline-offset:4px}header{max-width:1050px;margin:auto;padding:55px 28px 30px}.eyebrow{font-size:12px;letter-spacing:2px;color:var(--teal);text-transform:uppercase}h1{font-size:42px;line-height:1.3;letter-spacing:-1px;margin:15px 0}header p{max-width:720px;color:var(--muted)}.meta{font-size:13px}.actions{display:flex;gap:10px;flex-wrap:wrap}.actions a,.actions button{border:1px solid var(--line);background:white;padding:8px 16px;border-radius:6px;color:var(--ink);font:inherit;text-decoration:none;cursor:pointer}.toolbar{position:sticky;top:0;background:#faf8f3f5;z-index:5;border-block:1px solid var(--line);padding:14px 24px}.controls{max-width:994px;margin:auto;display:flex;gap:12px;align-items:center;flex-wrap:wrap}input,select{font:inherit;min-width:0;border:1px solid #aebabe;padding:9px 12px;border-radius:5px;background:#fff;color:var(--ink)}input{flex:1}#count{font-size:13px;color:var(--muted)}main{max-width:1050px;margin:auto;padding:20px 28px 60px}.chapter{margin:35px 0 15px;border-bottom:2px solid var(--teal);padding-bottom:10px;font-size:25px}.entry{margin:0;padding:25px 0 30px;border-bottom:1px solid var(--line)}.entry>h3{font-size:22px;line-height:1.6;margin:0 0 16px}.number{color:var(--teal);font-size:14px;display:block;letter-spacing:1px}.entry p{margin:10px 0}.label{font-weight:600}.evidence{background:#eef2ee;padding:14px 18px;margin-top:18px;border-left:3px solid var(--teal);font-size:14px;color:#41545d}.evidence p{margin:5px 0}details{margin:18px 0}summary{cursor:pointer;font-weight:600;padding:12px 0}details[open] summary{border-bottom:1px solid var(--line)}.document{padding:10px 0}.document h2{font-size:28px}.document h3{font-size:22px}.document h4{font-size:19px}table{border-collapse:collapse;width:100%;font-size:14px}td,th{border-bottom:1px solid var(--line);padding:10px;text-align:left;vertical-align:top}th{background:#e8eeeb}.table-scroll{overflow-x:auto}.bullet{padding-left:18px;position:relative}.bullet:before{content:'•';position:absolute;left:0}blockquote{margin:15px 0;padding:12px 18px;border-left:3px solid var(--teal);background:#eef2ee}code,pre{background:#eef0ec;font-size:14px}pre{padding:14px;overflow:auto}footer{border-top:1px solid var(--line);padding:25px 28px;color:var(--muted);font-size:13px}#empty{padding:35px 0}.hidden{display:none!important}@media(max-width:650px){h1{font-size:31px}header{padding-top:32px}.entry>h3{font-size:20px}main{padding-inline:20px}.toolbar{padding-inline:20px}select{width:100%}}@media print{body{background:#fff;font-size:10pt;line-height:1.7}header{padding:0}h1{font-size:28pt}.toolbar,.actions,.meta,#empty{display:none}main{padding:0;max-width:none}.chapter{break-before:page}.entry h3{break-after:avoid}[data-section].hidden,.entry.hidden{display:block!important}#empty{display:none!important}details{display:block}summary{display:none}a{color:inherit}footer{display:none}@page{size:A4;margin:18mm}}

.entry h4{font-size:18px;margin:23px 0 10px}.contents{padding:18px 22px;background:#eef2ee}.contents ul{list-style:none;padding:0;margin:5px 0 16px}.contents li{margin:4px 0}.contents .sub{font-size:14px;margin-left:16px}.chapter-lead{color:var(--muted)}.entry .evidence{font-size:14px}
'''
JS='''
const input=document.querySelector('#search'),select=document.querySelector('#chapter-filter');
const entries=[...document.querySelectorAll('.entry')];
const continuous=document.body.classList.contains('continuous');
const normalize=s=>s.normalize('NFKC').toLowerCase().replace(/\\s+/g,' ').trim();
function filter(){const terms=normalize(input.value).split(' ').filter(Boolean);let count=0;
for(const e of entries){const ok=(!select.value||e.dataset.chapter===select.value)&&terms.every(t=>normalize(e.textContent).includes(t));e.classList.toggle('hidden',!ok);if(ok)count++}
for(const c of document.querySelectorAll('[data-section]'))c.classList.toggle('hidden',![...c.querySelectorAll('.entry')].some(e=>!e.classList.contains('hidden')));
document.querySelector('#count').textContent=`${count} / ${entries.length} 节`;document.querySelector('#empty').classList.toggle('hidden',count>0);
const params=new URLSearchParams();if(input.value)params.set('q',input.value);if(select.value)params.set('chapter',select.value);try{history.replaceState(null,'',location.pathname+(params.size?'?'+params:'')+location.hash)}catch{}
}
function restoreFilters(){const params=new URLSearchParams(location.search);input.value=continuous?'':params.get('q')||'';select.value=continuous?'':params.get('chapter')||'';filter()}
if(continuous)document.querySelectorAll('details').forEach(d=>d.open=true);
input.addEventListener('input',filter);select.addEventListener('change',filter);restoreFilters();
const toolbar=document.querySelector('.toolbar');
function updateAnchorOffset(){document.documentElement.style.setProperty('--anchor-offset',`${Math.ceil(toolbar.getBoundingClientRect().height)+16}px`)}
updateAnchorOffset();window.addEventListener('resize',updateAnchorOffset);
if(typeof ResizeObserver!=='undefined')new ResizeObserver(updateAnchorOffset).observe(toolbar);
document.querySelector('#reset').addEventListener('click',()=>{input.value='';select.value='';filter()});
let printState=null;
function preparePrint(){if(printState)return;printState=[...document.querySelectorAll('details')].map(d=>[d,d.open]);for(const [d] of printState)d.open=true}
function finishPrint(){if(!printState)return;for(const [d,open] of printState)d.open=open;printState=null}
window.addEventListener('beforeprint',preparePrint);window.addEventListener('afterprint',finishPrint);
document.querySelector('#print').addEventListener('click',()=>{preparePrint();window.print()});
function revealHash(hash=location.hash){if(!hash)return;let target;try{target=document.getElementById(decodeURIComponent(hash.slice(1)))}catch{return}if(!target)return;input.value='';select.value='';filter();let p=target;while(p){if(p.tagName==='DETAILS')p.open=true;p=p.parentElement}requestAnimationFrame(()=>target.scrollIntoView())}
document.addEventListener('click',event=>{if(event.defaultPrevented||event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;const link=event.target.closest?.('a[href^="#"]');if(!link)return;const hash=link.getAttribute('href');let target;try{target=document.getElementById(decodeURIComponent(hash.slice(1)))}catch{return}if(!target)return;event.preventDefault();if(location.hash!==hash)location.hash=hash;revealHash(hash)});
function restoreNavigation(){restoreFilters();if(!input.value&&!select.value)revealHash()}
window.addEventListener('popstate',restoreNavigation);window.addEventListener('hashchange',restoreNavigation);revealHash();
'''

def contents_html():
    out=['<nav class="contents" id="contents" aria-label="总目录"><h2>目录</h2>']
    for c in CHAPTERS:
        out.append(f'<a href="#chapter-{c["id"]}"><b>第 {c["id"]} 章 · {html.escape(c["title"])}</b></a><ul>')
        for e in c['entries']:out.append(f'<li class="sub"><a href="#entry-{e["id"]}">{e["id"]} {html.escape(e["title"])}</a></li>')
        out.append('</ul>')
    for i,name in enumerate(DOCS):
        text=(ROOT/'docs'/name).read_text();title=text.splitlines()[0].lstrip('# ');dest=PATHS['docs/'+name]
        out.append(f'<p><a href="{dest}">{html.escape(title)}</a></p>')
    return ''.join(out)+'</nav>'

def build_html():
    nav=''.join(f'<option value="{c["id"]}">第 {c["id"]} 章 · {html.escape(c["title"])}</option>' for c in CHAPTERS)
    author=META['author']
    accounts=''.join(f'<p><b>{html.escape(c["account_label"])}：{html.escape(c["account"])}</b></p>' for c in author['channels'])
    author_section=f'<details id="author"><summary>作者介绍</summary><div class="document"><h2>作者介绍</h2><div style="display:flex;gap:24px;align-items:center;flex-wrap:wrap"><img src="{html.escape(author["avatar"],quote=True)}" alt="{html.escape(author["name"]+" 的头像",quote=True)}" width="160" height="160" style="display:block;object-fit:contain;border-radius:12px"><div style="flex:1;min-width:200px"><p><b>{html.escape(author["name"])}</b></p><p>{html.escape(author["bio"])}</p>{accounts}</div></div></div></details>'
    body=[author_section,f'<details id="disclaimer"><summary>免责声明与阅读说明</summary><div class="document">{render_md(FRONT.read_text(),FRONT.parent,document=True)}</div></details>',contents_html(),f'<details id="reading-path" open><summary>阅读说明：从眼前的问题开始</summary><div class="document">{render_md(INTRO.read_text(),INTRO.parent,document=True)}</div></details>']
    for c in CHAPTERS:
        body.append(f'<section data-section><h2 class="chapter" id="chapter-{c["id"]}">第 {c["id"]} 章 · {html.escape(c["title"])}</h2><div class="chapter-lead">{render_md(c["lead"],c["path"].parent)}</div>')
        for e in c['entries']:body.append(f'<article class="entry" id="entry-{e["id"]}" data-chapter="{c["id"]}"><h3>{e["id"]} {html.escape(e["title"])}</h3>'+render_md(e['body'],c['path'].parent,entry=True)+'</article>')
        body.append('</section>')
    body.append('<p id="empty" class="hidden">没有匹配的正文节。试试更短的关键词，或清除章节筛选。</p>')
    for name in DOCS:
        path=ROOT/'docs'/name;text=path.read_text();title=text.splitlines()[0].lstrip('# ')
        body.append(f'<details id="{PATHS["docs/"+name][1:]}"><summary>{html.escape(title)}</summary><div class="document">{render_md(text,path.parent,document=True)}</div></details>')
    page=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{META['title']}</title><style>{CSS}</style></head><body>
<header id="about"><div class="eyebrow">HOW TO LIVE WITH AI / 青年建议与基础教学</div><h1>{META['title']}</h1><p>{META['subtitle']}。按六章主线阅读，也可以从眼前的问题开始。</p><p class="meta">v{META['version']} · {META['date']} · 6 章 / 29 节 · 4 个附录 · {META['status']}</p><blockquote><b>免责声明：学习参考。</b> {html.escape(META['disclaimer'])} <a href="#disclaimer">完整说明</a></blockquote><div class="actions"><a href="#contents">总目录</a><a href="#chapter-1">认识 AI</a><a href="#chapter-3">学什么</a><a href="#chapter-4">开始行动</a><a href="{META['pdf']}">下载 PDF</a><a href="阅读全文.html">连续阅读</a><a href="{META['cover']}">封面图片</a><button id="print">打印 / 保存 PDF</button></div></header>
<div class="toolbar"><div class="controls"><input id="search" type="search" aria-label="搜索正文" placeholder="搜索正文：任务、学习、方向…"><select id="chapter-filter" aria-label="选择章节"><option value="">全部章节</option>{nav}</select><button id="reset">清除筛选</button><span id="count" aria-live="polite"></span></div></div>
<main>{''.join(body)}</main><footer>正文、示例与练习为本项目编写；研究、官方资料与作者建议分别标注。附录可展开阅读或用浏览器页面查找。原创内容采用 CC BY 4.0，第三方资料按原许可处理。维护记录保留在仓库。</footer><script>{JS}</script></body></html>'''
    (ROOT/'index.html').write_text(page)
    continuous=page.replace('<body>','<body class="continuous">').replace('<style>','<style>.continuous .toolbar{display:none}')
    (ROOT/'阅读全文.html').write_text(continuous)
    return page

class GuideDoc(BaseDocTemplate):
    def afterFlowable(self,f):
        if isinstance(f,Paragraph) and getattr(f,'bookmark',None):
            key=f.bookmark;level=f.outline_level
            self.canv.bookmarkHorizontalAbsolute(key,self.frame._y+f.height)
            self.canv.addOutlineEntry(f.getPlainText(),key,level,False)
            if key!='contents':self.notify('TOCEntry',(level,f.getPlainText(),self.page,key))

def build_pdf(font,bold):
    pdfmetrics.registerFont(TTFont('Guide',font,subfontIndex=0));pdfmetrics.registerFont(TTFont('GuideBold',bold,subfontIndex=0))
    pdfmetrics.registerFontFamily('Guide',normal='Guide',bold='GuideBold',italic='Guide',boldItalic='GuideBold')
    styles={
      'p':ParagraphStyle('body',fontName='Guide',fontSize=10.5,leading=17,textColor=colors.HexColor('#1c2b36'),spaceAfter=7,wordWrap='CJK'),
      'h1':ParagraphStyle('chapter',fontName='GuideBold',fontSize=23,leading=32,spaceAfter=20,keepWithNext=True,wordWrap='CJK'),
      'h2':ParagraphStyle('section',fontName='GuideBold',fontSize=15,leading=23,spaceBefore=15,spaceAfter=10,keepWithNext=True,textColor=colors.HexColor('#235e67'),wordWrap='CJK'),
      'h3':ParagraphStyle('subsection',fontName='GuideBold',fontSize=12,leading=19,spaceBefore=13,spaceAfter=8,keepWithNext=True,wordWrap='CJK'),
      'small':ParagraphStyle('small',fontName='Guide',fontSize=9,leading=14.8,spaceAfter=7,textColor=colors.HexColor('#51656c'),wordWrap='CJK'),
      'cell':ParagraphStyle('cell',fontName='Guide',fontSize=8.5,leading=13,wordWrap='CJK')}
    w,h=A4;output=ROOT/META['pdf'];output.parent.mkdir(exist_ok=True)
    cover_path=ROOT/META.get('pdf_cover',META['cover'])
    image_w,image_h=ImageReader(str(cover_path)).getSize()
    # PDF needs its own portrait composition; a fitted web banner leaves large
    # empty bands even when the page size itself is correct.
    if abs((image_w/image_h)/(w/h)-1)>.02:
        raise ValueError('PDF cover artwork must have a portrait A4 aspect ratio')
    cover_scale=min(w/image_w,h/image_h)
    cover_w,cover_h=image_w*cover_scale,image_h*cover_scale
    cover_x,cover_y=(w-cover_w)/2,(h-cover_h)/2
    def decorate(canvas,doc):
        if doc.page==1:
            canvas.drawImage(str(cover_path),cover_x,cover_y,width=cover_w,height=cover_h,preserveAspectRatio=True,anchor='c')
            return
        canvas.saveState();canvas.setStrokeColor(colors.HexColor('#d6dfdc'));canvas.line(48,h-41,w-48,h-41)
        canvas.setFont('Guide',8);canvas.setFillColor(colors.HexColor('#5a6a71'));canvas.drawString(48,h-31,META['title'])
        canvas.drawRightString(w-48,28,f'v{META["version"]} · {META["date"]}  /  {doc.page}');canvas.restoreState()
    doc=GuideDoc(str(output),pagesize=A4,title=META['title'],author=META['author']['name'],leftMargin=48,rightMargin=48,topMargin=61,bottomMargin=48)
    doc.addPageTemplates([
        PageTemplate(id='cover',frames=[Frame(0,0,w,h,id='cover-body',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=decorate,pagesize=A4),
        PageTemplate(id='main',frames=[Frame(48,48,w-96,h-109,id='body',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=decorate,pagesize=A4)
    ])
    def para(text,style='p',base=ROOT):return Paragraph(inline(text,base,pdf=True),styles[style])
    def heading(text,key,level=0):
        f=para(text,'h1' if level==0 else 'h2');f.bookmark=key;f.outline_level=level;return f
    def flows(text,base,key=None):
        result=[];pending=None
        for kind,v in blocks(text):
            if kind=='anchor':pending=v;continue
            if kind=='h1':result.append(heading(v,key));continue
            if kind in ['h2','h3']:
                f=para(v,kind,base)
                if pending:
                    f=Paragraph(f'<a name="{pending}"/>'+inline(v,base,pdf=True),styles[kind])
                    if kind=='h2' and re.match(r'^[A-D]\.\d+ ',v):f.bookmark=pending;f.outline_level=1
                    pending=None
                result.append(f)
            elif kind=='table':
                cols=max(map(len,v));rows=[[para(cell,'cell',base) for cell in row]+['']*(cols-len(row)) for row in v]
                table=Table(rows,colWidths=[(w-96)/cols]*cols,repeatRows=1,hAlign='LEFT')
                table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8eeeb')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-1),.4,colors.HexColor('#d6dfdc')),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
                result.extend([table,Spacer(1,10)])
            elif kind=='code':result.append(Paragraph(inline(v,base,pdf=True).replace('\n','<br/>'),styles['small']))
            else:
                style='small' if v.startswith('**依据与范围：**') else 'p'
                result.append(para(('• ' if kind=='li' else '')+v,style,base))
        return result
    story=[Spacer(1,1),NextPageTemplate('main'),PageBreak()]
    author=META['author']
    iw,ih=ImageReader(str(ROOT/author['avatar'])).getSize();scale=min(230/iw,230/ih)
    avatar=Image(str(ROOT/author['avatar']),width=iw*scale,height=ih*scale,hAlign='CENTER')
    profile_name=ParagraphStyle('profile-name',parent=styles['h2'],alignment=1,fontSize=21,leading=30,spaceBefore=0)
    profile_bio=ParagraphStyle('profile-bio',parent=styles['p'],alignment=1,leading=20)
    profile_account=ParagraphStyle('profile-account',parent=styles['h2'],alignment=1,spaceBefore=0,spaceAfter=0)
    account_text='<br/>'.join(inline(c['account_label']+'：'+c['account'],ROOT,pdf=True) for c in author['channels'])
    account_box=Table([[Paragraph(account_text,profile_account)]],colWidths=[330],hAlign='CENTER')
    account_box.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#eef3f5')),('BOX',(0,0),(-1,-1),.5,colors.HexColor('#d6dfdc')),('TOPPADDING',(0,0),(-1,-1),16),('BOTTOMPADDING',(0,0),(-1,-1),16)]))
    story.extend([heading('作者介绍','author'),Spacer(1,20),avatar,Spacer(1,22),Paragraph(html.escape(author['name']),profile_name),Paragraph(html.escape(author['bio']),profile_bio),Spacer(1,16),account_box,PageBreak()])
    story.extend(flows(FRONT.read_text(),FRONT.parent,'disclaimer'));story.append(PageBreak())
    story.append(heading('目录','contents'))
    toc=TableOfContents();toc.levelStyles=[ParagraphStyle('toc0',fontName='GuideBold',fontSize=10.5,leading=17,spaceBefore=7,wordWrap='CJK'),ParagraphStyle('toc1',fontName='Guide',fontSize=9.5,leading=15,leftIndent=14,spaceBefore=2,wordWrap='CJK')]
    story.extend([toc,PageBreak()]);story.extend(flows(INTRO.read_text(),INTRO.parent,'reading-path'));story.append(PageBreak())
    for c in CHAPTERS:
        story.append(heading(f'第 {c["id"]} 章 · {c["title"]}',f'chapter-{c["id"]}'))
        story.extend(flows(c['lead'],c['path'].parent))
        for e in c['entries']:
            story.append(heading(f'{e["id"]} {e["title"]}',f'entry-{e["id"]}',1));story.extend(flows(e['body'],c['path'].parent))
        story.append(PageBreak())
    for i,name in enumerate(DOCS):
        path=ROOT/'docs'/name;fs=flows(path.read_text(),path.parent,PATHS['docs/'+name][1:])
        # Short source records stay together; chapter-sized sections remain splittable.
        def append_record(record):
            height=sum(f.wrap(w-96,h-109)[1]+f.getSpaceBefore()+f.getSpaceAfter() for f in record)
            if height>240:story.extend(record)
            else:story.append(KeepTogether(record))
        group=[]
        for f in fs:
            is_source=isinstance(f,Paragraph) and re.match(r'^(R|P|M|C|L)\d+ ·',f.getPlainText())
            is_heading=isinstance(f,Paragraph) and f.style.name in ['chapter','section','subsection']
            if group and is_heading:append_record(group);group=[]
            if is_source:
                lead=[]
                if story and isinstance(story[-1],Paragraph) and story[-1].style.name=='section':lead=[story.pop()]
                group=lead+[f]
            elif group:group.append(f)
            else:story.append(f)
        if group:append_record(group)
        if i<len(DOCS)-1:story.append(PageBreak())
    doc.multiBuild(story);return output

def merged_md(path):
    def rewrite(m):
        label,url=m.groups()
        if urlsplit(url).scheme or url.startswith('#'):return m[0]
        file,sep,anchor=url.partition('#');dest=(path.parent/file).resolve().relative_to(ROOT).as_posix()
        return f'[{label}]({dest}'+(sep+anchor if sep else '')+')'
    return LINK.sub(rewrite,path.read_text())

def reading_paths():return [FRONT,INTRO]+[c['path'] for c in CHAPTERS]+[ROOT/'docs'/n for n in DOCS]

def author_markdown():
    author=META['author'];lines=['## 作者介绍','',f'![{author["name"]} 的头像]({author["avatar"]})','',f'**{author["name"]}**','',author['bio'],'']
    for channel in author['channels']:
        lines.extend([f'{channel["account_label"]}：{channel["account"]}',''])
    return '\n'.join(lines)

def markdown_contents():
    lines=['## 目录']
    for c in CHAPTERS:
        path=c['path'].relative_to(ROOT).as_posix();lines.append(f'- [第 {c["id"]} 章 · {c["title"]}]({path})')
        lines.extend(f'- [{e["id"]} {e["title"]}]({path}#entry-{e["id"]})' for e in c['entries'])
    for n in DOCS:
        title=(ROOT/'docs'/n).read_text().splitlines()[0].lstrip('# ');lines.append(f'- [{title}](docs/{n})')
    return '\n'.join(lines)

def validate(page):
    manifest=json.loads((ROOT/'downloads/build-manifest.json').read_text())
    for group in ['sources','outputs']:
        for name,digest in manifest[group].items():
            if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest:raise ValueError(f'{group}: stale file {name}')
    if set(manifest['outputs'])!={'index.html','阅读全文.html','完整指南.md',META['pdf']}:raise ValueError('Incomplete output manifest')
    if 'class="continuous"' not in (ROOT/'阅读全文.html').read_text():raise ValueError('Continuous mode missing')
    if re.findall(r'<h1[^>]*>(.*?)</h1>',page)!=[html.escape(META['title'])]:raise ValueError('HTML must have a single handbook-level title')
    ids=re.findall(r'\bid="([^"]+)"',page)
    if len(set(ids))!=len(ids):raise ValueError('Duplicate HTML anchors')
    expected=[e['id'] for e in ENTRIES]
    order=['author','disclaimer','contents','reading-path']+[f'chapter-{i}' for i in range(1,7)]+['appendix-a','appendix-b','appendix-c','appendix-d','copyright']
    positions=[page.index(f'id="{key}"') for key in order]
    if positions!=sorted(positions):raise ValueError('HTML document order differs')
    if re.findall(r'<article class="entry" id="entry-(\d+\.\d+)"',page)!=expected:raise ValueError('HTML section order differs')
    for target in re.findall(r'href="([^"]+)"',page):
        target=html.unescape(target)
        if target.startswith('#') and target[1:] not in ids:raise ValueError('Missing HTML anchor '+target)
        if not urlsplit(target).scheme and not target.startswith('#') and not (ROOT/target).exists():raise ValueError('Missing file '+target)
    for p in reading_paths():
        for _,url in LINK.findall(p.read_text()):
            if urlsplit(url).scheme:continue
            file,sep,anchor=url.partition('#');dest=(p.parent/file).resolve() if file else p
            if not dest.exists():raise ValueError(f'{p.name}: missing {url}')
            if sep and anchor not in re.findall(r'<a id="([^"]+)"',dest.read_text()):raise ValueError(f'{p.name}: missing source anchor {url}')
    for prefix,count in [('r',34),('p',19),('m',5),('c',1),('l',1)]:
        if {x for x in ids if re.fullmatch(prefix+r'\d+',x)}!={f'{prefix}{i:02}' for i in range(1,count+1)}:raise ValueError('Source identifier coverage '+prefix)
    merged=(ROOT/'完整指南.md').read_text()
    if author_markdown() not in merged:raise ValueError('Merged Markdown author missing')
    author_html=page.split('<details id="author">',1)[1].split('</details>',1)[0]
    if f'src="{META["author"]["avatar"]}"' not in author_html or author_html.count('<img ')!=1:
        raise ValueError('HTML author must contain exactly one avatar')
    for channel in META['author']['channels']:
        if channel['account'] not in author_html:
            raise ValueError('HTML author channel missing')
    for p in reading_paths():
        if merged_md(p) not in merged:raise ValueError('Merged Markdown incomplete '+p.name)
    reader=PdfReader(ROOT/META['pdf']);text='\n'.join(p.extract_text() or '' for p in reader.pages)
    for number,p in enumerate(reader.pages,1):
        for box in (p.mediabox,p.cropbox):
            if any(abs(float(value)-expected)>.01 for value,expected in zip(box,(0,0,*A4))) or p.rotation%360:
                raise ValueError(f'PDF page {number}: expected unrotated portrait A4')
    cover_images=[x.get_object() for x in reader.pages[0]['/Resources'].get('/XObject',{}).values() if x.get_object().get('/Subtype')=='/Image']
    if len(cover_images)!=1 or abs((float(cover_images[0]['/Width'])/float(cover_images[0]['/Height']))/(A4[0]/A4[1])-1)>.02:
        raise ValueError('PDF cover artwork must have a portrait A4 aspect ratio')
    cover_ops=reader.pages[0].get_contents().operations
    draws=[i for i,(_,op) in enumerate(cover_ops) if op==b'Do']
    if len(draws)!=1 or draws[0]==0 or cover_ops[draws[0]-1][1]!=b'cm':
        raise ValueError('PDF cover image placement missing')
    iw,b,c,ih,x,y=map(float,cover_ops[draws[0]-1][0]);pw,ph=A4
    if abs(b)+abs(c)>.01 or iw<=0 or ih<=0 or x<-.01 or y<-.01 or x+iw>pw+.01 or y+ih>ph+.01 or iw*ih/(pw*ph)<.98:
        raise ValueError('PDF cover must fill the page without clipping')
    if abs(iw/ih-float(cover_images[0]['/Width'])/float(cover_images[0]['/Height']))>1e-5:
        raise ValueError('PDF cover image is stretched')
    def flatten(items):
        return [item for x in items for item in (flatten(x) if isinstance(x,list) else [x])]
    outlines=flatten(reader.outline);titles=[x['/Title'] for x in outlines]
    bodytitles=[f'{e["id"]} {e["title"]}' for e in ENTRIES]
    if [t for t in titles if re.match(r'^\d+\.\d+ ',t)]!=bodytitles:raise ValueError('PDF section bookmarks differ')
    if titles[:2]!=['作者介绍','免责声明与阅读说明'] or titles[-1]!='版权与使用说明':raise ValueError('Front/back bookmark order')
    if reader.get_destination_page_number(outlines[0])!=1 or reader.get_destination_page_number(outlines[1])!=2:
        raise ValueError('Author and disclaimer must be on pages 2 and 3')
    author_text=reader.pages[1].extract_text() or ''
    author_images=[x.get_object() for x in reader.pages[1]['/Resources'].get('/XObject',{}).values() if x.get_object().get('/Subtype')=='/Image']
    if len(author_images)!=1 or any(c['account'] not in author_text for c in META['author']['channels']):
        raise ValueError('PDF author must contain one avatar and account numbers')
    avatar_size=ImageReader(str(ROOT/META['author']['avatar'])).getSize()
    if tuple(int(author_images[0][k]) for k in ('/Width','/Height'))!=avatar_size:
        raise ValueError('PDF author avatar dimensions differ from source')
    for title in titles:
        if title.replace(' ','') not in text.replace(' ','').replace('\n',''):raise ValueError('PDF title missing '+title)
    for x in outlines:
        dest=reader.get_destination_page_number(x)
        if dest is None or not 0<=dest<len(reader.pages):raise ValueError('Invalid bookmark destination')
        if x['/Title'].replace(' ','') not in (reader.pages[dest].extract_text() or '').replace(' ','').replace('\n',''):raise ValueError('Bookmark title absent at target '+x['/Title'])
    links=sum(1 for p in reader.pages for ref in p.get('/Annots',[]) if ref.get_object().get('/A',{}).get('/URI'))
    internal=sum(1 for p in reader.pages for ref in p.get('/Annots',[]) if ref.get_object().get('/Dest'))
    if not links or not internal:raise ValueError('PDF source/internal links missing')
    print(json.dumps({'chapters':len(CHAPTERS),'sections':len(ENTRIES),'appendices':4,'pdf_pages':len(reader.pages),'bookmarks':len(outlines),'source_links':links,'internal_links':internal,'source_records':60,'links_and_source_coverage':'passed'},ensure_ascii=False))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');parser.add_argument('--font',default='/System/Library/Fonts/STHeiti Light.ttc');parser.add_argument('--bold-font',default='/System/Library/Fonts/STHeiti Medium.ttc');args=parser.parse_args()
    if args.check:validate((ROOT/'index.html').read_text());return
    page=build_html();build_pdf(args.font,args.bold_font)
    merged=f'# {META["title"]}\n\nv{META["version"]} · {META["date"]}\n\n'+author_markdown()+'\n\n'+merged_md(FRONT)+'\n\n'+markdown_contents()+'\n\n'+ '\n\n'.join(merged_md(p) for p in reading_paths()[1:])
    (ROOT/'完整指南.md').write_text(merged)
    inputs=[ROOT/'project.json',ROOT/'tools/build_release.py',ROOT/META['cover'],ROOT/META.get('pdf_cover',META['cover']),ROOT/META['author']['avatar']]+reading_paths()
    sources_hash={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    outputs={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['index.html','阅读全文.html','完整指南.md',META['pdf']]}
    (ROOT/'downloads/build-manifest.json').write_text(json.dumps({'version':META['version'],'date':META['date'],'sources':sources_hash,'outputs':outputs},ensure_ascii=False,indent=2))
    validate(page)
if __name__=='__main__':main()
