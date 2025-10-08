import os, time, csv, re
from typing import List, Dict, Any
from parsers import parse_telegram_channel, parse_getmatch_page, parse_linkedin_search
from dotenv import load_dotenv

load_dotenv()

KEYWORDS = [k.strip() for k in os.getenv('KEYWORDS','Commercial Analyst,Growth Analyst,Partner Performance Analyst').split(',') if k.strip()]
COUNTRIES = [c.strip() for c in os.getenv('COUNTRIES','').split(',') if c.strip()]

def normalize_url(u: str) -> str:
    return u.split('?')[0].strip()

def harvest_once() -> List[Dict[str,Any]]:
    items = []
    # LinkedIn best-effort
    linkedin_q = ' '.join(KEYWORDS[:3])
    try:
        items += parse_linkedin_search(linkedin_q)
    except Exception as e:
        print('LinkedIn parse failed:', e)
    # Telegram channels
    channels = ['foranalysts','geekjobs','remotegeekjob','zarubezhom_jobs']
    for ch in channels:
        try:
            items += parse_telegram_channel(ch)
            time.sleep(1.0)
        except Exception as e:
            print('tg parse failed', ch, e)
    # GetMatch pages (first 3 pages)
    for p in range(1,4):
        try:
            items += parse_getmatch_page(p)
            time.sleep(0.8)
        except Exception as e:
            print('getmatch parse failed page', p, e)

    # post-filter by keywords and dedupe
    filtered = []
    seen = set()
    for it in items:
        text = (it.get('title','') + ' ' + it.get('snippet','') + ' ' + it.get('company','')).lower()
        if any(kw.lower().split()[0] in text for kw in KEYWORDS):
            url = normalize_url(it.get('url',''))
            if url in seen: continue
            seen.add(url)
            filtered.append(it)
    return filtered

def save_csv(items: List[Dict[str,Any]], path='data/jobs.csv'):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    exists = os.path.exists(path)
    with open(path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['date','title','company','location','source','url','snippet'])
        if not exists:
            writer.writeheader()
        for it in items:
            writer.writerow({
                'date': it.get('date',''),
                'title': it.get('title',''),
                'company': it.get('company',''),
                'location': it.get('location',''),
                'source': it.get('source',''),
                'url': it.get('url',''),
                'snippet': it.get('snippet',''),
            })
