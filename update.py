"""Actualiza la base pública de noticias RSS. No inventa contenido ni usa IA."""
from __future__ import annotations
import json, os, re, html, hashlib
from pathlib import Path
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlencode
from zoneinfo import ZoneInfo
import requests, feedparser

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
DATA.mkdir(exist_ok=True)
TZ = ZoneInfo('America/Santiago')
NOW = datetime.now(timezone.utc)
# Google News RSS es una interfaz no documentada: puede cambiar.
QUERIES = {
 'chile': [('("energía" OR "eléctrico" OR "BESS") (Chile OR SEN OR CEN) when:2d', 'es-419','CL','CL:es-419'), ('"Coordinador Eléctrico" OR "CNE" OR "energía solar" Chile when:2d','es-419','CL','CL:es-419')],
 'global': [('renewable energy battery storage power grids utilities when:2d','en-US','US','US:en'), ('solar wind electricity market investment IEA when:2d','en-US','US','US:en')],
 'ia': [('artificial intelligence OpenAI Anthropic Google DeepMind models agents when:2d','en-US','US','US:en'), ('AI data centers electricity demand infrastructure when:2d','en-US','US','US:en')],
 'geopolitica': [('geopolitics energy security oil gas trade sanctions when:2d','en-US','US','US:en')],
}
TARGET = {'chile': 4, 'global': 4, 'ia': 5, 'geopolitica': 2}
LABEL = {'chile':'Energía Chile','global':'Energía internacional','ia':'Inteligencia artificial','geopolitica':'Geopolítica'}
KEYWORDS = {
 'chile':['chile','eléctr','energ','cen','cne','bess','solar','transmisi','generaci'],
 'global':['power','energy','solar','wind','battery','grid','electricity','storage','renewable','nuclear'],
 'ia':[' ai ','artificial intelligence','openai','anthropic','deepmind','model','agent','datacenter','data center'],
 'geopolitica':['geopolit','sanction','tariff','oil','gas','war','trade','security','opec'],
}
WATCH = {
 'chile':'Seguimiento sugerido: efecto sobre costos marginales, operación del SEN, inversión, regulación o almacenamiento. No se infiere un efecto causal sin contrastar el artículo.',
 'global':'Seguimiento sugerido: escalabilidad tecnológica, CAPEX, redes, flexibilidad y posibles implicancias para Chile.',
 'ia':'Seguimiento sugerido: capacidades técnicas, automatización, costos computacionales, consumo eléctrico y aplicaciones al sector energético.',
 'geopolitica':'Seguimiento sugerido: cadenas de suministro, mercados de combustibles, inversión y seguridad energética.'
}

def clean(s):
 s = re.sub(r'<[^>]+>', ' ', s or '')
 return re.sub(r'\s+', ' ', html.unescape(s)).strip()

def make_feed(query,lang,region,edition):
 return 'https://news.google.com/rss/search?' + urlencode({'q':query,'hl':lang,'gl':region,'ceid':edition})

def published(entry):
 for field in ('published','updated'):
  try:
   d=parsedate_to_datetime(entry.get(field,''))
   return d.astimezone(timezone.utc) if d.tzinfo else d.replace(tzinfo=timezone.utc)
  except (ValueError,TypeError,IndexError): pass
 return None

def fetch(cat):
 items=[]
 for query,lang,region,edition in QUERIES[cat]:
  url=make_feed(query,lang,region,edition)
  try:
   resp=requests.get(url, timeout=25, headers={'User-Agent':'EnergyIntelligenceHub/1.0 RSS reader'})
   resp.raise_for_status()
   feed=feedparser.parse(resp.content)
  except (requests.RequestException,Exception) as exc:
   print('Feed failed:',cat,str(exc)[:100]);continue
  for e in feed.entries[:35]:
   date=published(e)
   if date is None or not (NOW-timedelta(hours=54)<=date<=NOW+timedelta(hours=2)):continue
   title=clean(e.get('title',''))
   source=clean(e.get('source',{}).get('title','')) or 'Fuente indicada en Google News'
   # En Google News el título suele incluir ' - Medio'.
   if source and title.lower().endswith(' - '+source.lower()): title=title[:-(len(source)+3)]
   link=e.get('link','')
   if not title or not link.startswith('https://'):continue
   excerpt=clean(e.get('summary',''))
   excerpt=re.sub(r'\s*'+re.escape(title)+r'\s*',' ',excerpt,flags=re.I).strip() if excerpt else ''
   hay=(title+' '+excerpt).lower()
   score=sum(1 for word in KEYWORDS[cat] if word in hay)
   h=hashlib.sha256(re.sub(r'[^a-z0-9]','',title.lower()).encode()).hexdigest()[:16]
   items.append({'id':h,'category':cat,'category_label':LABEL[cat], 'title':title,
                 'source':source, 'published_at':date.isoformat(),
                 'url':link,'url_type':'Google News (enlace al artículo)',
                 'summary':excerpt[:450] or 'Abrir el enlace para revisar el artículo completo.',
                 'impact':WATCH[cat], 'analysis_type':'Pistas técnicas para investigar, no conclusiones verificadas',
                 'score':score})
 return items

def main():
 chosen=[]; seen=set(); stats={}
 for category,count in TARGET.items():
  candidates=fetch(category)
  candidates.sort(key=lambda a:(a['score'],a['published_at']),reverse=True)
  picked=[]
  for x in candidates:
   if x['id'] in seen:continue
   seen.add(x['id']);picked.append(x)
   if len(picked)>=count:break
  chosen.extend(picked);stats[category]={'found':len(candidates),'selected':len(picked),'target':count}
 payload={'updated_at':datetime.now(TZ).isoformat(timespec='seconds'), 'timezone':'America/Santiago',
          'method':'Titulares y extractos de Google News RSS; sin resumen generado por IA; sin verificación manual del artículo completo',
          'requested_total':15,'actual_total':len(chosen),'counts':stats,'items':chosen}
 (DATA/'latest.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
 if chosen:
  stamp=datetime.now(TZ).date().isoformat()
  (DATA/f'{stamp}.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
 dates=sorted((x.stem for x in DATA.glob('20??-??-??.json')), reverse=True)
 (DATA/'history.json').write_text(json.dumps({'dates':dates[:365]},ensure_ascii=False,indent=2),encoding='utf-8')
 print('Actualizado:',len(chosen),'de 15 noticias; desglose:',stats)

if __name__=='__main__':main()
