#!/usr/bin/env python3
"""Import the bilingual LaTeX CV into the site's editable JSON data."""
import html
import json
import re
import shutil
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parents[1]
CV = Path(sys.argv[1]).resolve()

def arg(text, pos):
    while pos < len(text) and text[pos].isspace():
        pos += 1
    assert text[pos] == '{', text[pos:pos+70]
    start, depth = pos + 1, 1
    pos += 1
    while depth:
        if text[pos] == '\\':
            pos += 2
            continue
        if text[pos] == '{': depth += 1
        if text[pos] == '}': depth -= 1
        pos += 1
    return text[start:pos-1], pos

def tex(text):
    text = text.replace(r'{\l}', 'ł').replace(r'\"o', 'ö')
    out, i = [], 0
    wrappers = {'textbf': ('<strong>', '</strong>'), 'cvvalue': ('<strong>', '</strong>'),
                'textit': ('<em>', '</em>'), 'emph': ('<em>', '</em>'),
                'textsuperscript': ('<sup>', '</sup>'), 'cvbullet': ('<p>', '</p>')}
    while i < len(text):
        if text[i] == '\\':
            m = re.match(r'\\([a-zA-Z]+)', text[i:])
            if m:
                command = m[1]; i += len(m[0])
                if command in wrappers:
                    v, i = arg(text, i); a, b = wrappers[command];out.append(a+tex(v)+b)
                elif command == 'href':
                    url,i=arg(text,i);v,i=arg(text,i)
                    out.append('<a href="'+html.escape(url,quote=True)+'">'+tex(v)+'</a>')
                elif command == 'metasep': out.append(' · ')
                elif command == 'par': out.append(' ')
                else: raise ValueError('Unrecognized TeX command: '+command)
            else:
                i += 1
                if i < len(text): out.append(html.escape(text[i]));i+=1
        elif text[i] in '{}': i += 1
        elif text[i] == '~': out.append(' ');i+=1
        else: out.append(html.escape(text[i]));i+=1
    return ''.join(out).replace('---','—').replace('--','–').replace('``','“').replace("''",'”').strip()

def profile(path):
    sections=[];section=None;group=None
    for line in path.read_text().splitlines():
        if line.startswith(r'\begin{rSection}'):
            title,_=arg(line,len(r'\begin{rSection}'))
            section={'title':tex(title),'groups':[]};sections.append(section)
            group={'title':'','items':[]};section['groups'].append(group)
        elif line.startswith(r'\cvgroup'):
            title,_=arg(line,len(r'\cvgroup'))
            group={'title':tex(title),'items':[]};section['groups'].append(group)
        elif line.startswith(r'\cventry'):
            pos=len(r'\cventry');vals=[]
            for _ in range(5):
                v,pos=arg(line,pos);vals.append(tex(v))
            group['items'].append(dict(zip(['title','date','role','metrics','body'],vals)))
    for section in sections:
        section['groups']=[g for g in section['groups'] if g['items']]
    return sections

bib={}
for m in re.finditer(r'@(\w+)\{([^,]+),\n(.*?)\n\}',(CV/'references.bib').read_text(),re.S):
    entry={'type':m[1],'key':m[2]}
    entry.update({f[1]:f[2] for f in re.finditer(r'^\s*(\w+) = \{(.*)\},?$',m[3],re.M)})
    bib[m[2]]=entry
assert len(bib)==93

def citation(key,corresponding):
    e=bib[key];authors=[]
    for i,name in enumerate(e['author'].split(' and '),1):
        parts=name.split(', ',1); formatted=tex(' '.join(reversed(parts)))
        if name=='Feng, Chenyuan': formatted='<strong>'+formatted+'</strong>'
        if i in corresponding:formatted+='<sup>*</sup>'
        authors.append(formatted)
    author=', '.join(authors[:-1])+', and '+authors[-1] if len(authors)>1 else authors[0]
    title=tex(e['title']);link=e.get('url') or ('https://doi.org/'+e['doi'] if e.get('doi') else '')
    if link:title='<a href="'+html.escape(link,quote=True)+'">'+title+'</a>'
    venue=e.get('journal',e.get('booktitle',e.get('howpublished','')))
    venue=tex(venue)
    if not venue and e.get('eprint'):venue='arXiv:'+tex(e['eprint'])
    details=[]
    if e.get('volume'):
        v=e['volume']+('('+e['number']+')' if e.get('number') else '')
        if e.get('pages'):v+=':'+e['pages']
        details.append(tex(v))
    elif e.get('pages'):details.append('pp. '+tex(e['pages']))
    if e.get('publisher'):details.append(tex(e['publisher']))
    details.append(tex(e['year']))
    if e.get('note'):details.append(tex(e['note']))
    return author+'. '+title+'. '+('<em>'+venue+'</em>, ' if venue else '')+', '.join(details)+'.'

pubs=[]
for lang in ('en','zh'):
    sections=profile(CV/'sections'/lang/'profile.tex')+profile(CV/'sections'/lang/'engagement.tex')
    (SITE/'_data'/('cv_'+lang+'.json')).write_text(json.dumps(sections,ensure_ascii=False,indent=2)+'\n')
    groups=[];idx=-1
    for line in (CV/'sections'/lang/'publications.tex').read_text().splitlines():
        if line.startswith(r'\cvgroup'):
            title,_=arg(line,len(r'\cvgroup'));idx+=1
            groups.append({'id':['journals','conferences','books','demonstrations','preprints'][idx],
                'title':tex(title),'items':[]})
        elif line.strip().startswith(r'\cvpubitem'):
            raw,_=arg(line,line.index(r'\cvpubitem')+len(r'\cvpubitem'))
            match=re.search(r'\\bibentry\{([^}]+)\}',raw)
            metrics=''
            if r'\pubmetrics' in raw:
                metrics,_=arg(raw,raw.index(r'\pubmetrics')+len(r'\pubmetrics'))
            if match:
                cm=re.search(r'\\correspondingauthor\{([^}]+)\}',raw)
                cor=[int(n) for n in cm[1].split(',')] if cm else []
                item={'key':match[1],'html':citation(match[1],cor),'metrics':tex(metrics)}
            else:item={'key':'report-'+str(len(groups[idx]['items'])),'html':tex(raw),'metrics':''}
            groups[idx]['items'].append(item)
    assert sum(len(g['items']) for g in groups)==95
    (SITE/'_data'/('publications_'+lang+'.json')).write_text(json.dumps(groups,ensure_ascii=False,indent=2)+'\n')
    print(lang, len(sections), 'CV sections;',sum(len(g['items']) for g in groups),'publication entries')
(SITE/'assets/bibliography').mkdir(exist_ok=True)
shutil.copy2(CV/'references.bib',SITE/'assets/bibliography/references.bib')
