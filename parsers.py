import requests, time, re
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin, urlencode

HEADERS = {'User-Agent': 'JobHarvester/1.0 (+https://example.com)'}

def parse_telegram_channel(channel):
    # Parse public channel via t.me/s/<channel>
    url = f'https://t.me/s/{channel}'
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'lxml')
    posts = soup.select('div.tgme_widget_message')
    out = []
    for p in posts:
        date_el = p.select_one('time')
        date = date_el.get('datetime') if date_el else datetime.utcnow().isoformat()
        text = ' '.join([x.get_text(' ', strip=True) for x in p.select('div.tgme_widget_message_text *')])[:800]
        # look for first link
        a = p.select_one('a.tgme_widget_message_link') or p.select_one('a')
        link = a.get('href') if a else url
        title = text.split('\n')[0].strip()[:140]
        out.append({'date': date, 'title': title, 'company': '', 'location': 'remote', 'source': 'telegram/'+channel, 'url': link, 'snippet': text})
    return out

def parse_getmatch_page(page=1):
    url = f'https://getmatch.ru/vacancies?p={page}&sa=150000&l=remote&pa=all'
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'lxml')
    out = []
    cards = soup.select('div.vacancy__item, div.vacancy-card')
    if not cards:
        # fallback: search for links
        for a in soup.select('a[href]'):
            href = a.get('href')
            if '/vacancy/' in href:
                full = urljoin('https://getmatch.ru', href)
                out.append({'date': datetime.utcnow().isoformat(), 'title': a.get_text(strip=True)[:140], 'company':'', 'location':'remote', 'source':'getmatch', 'url':full, 'snippet': ''})
        return out
    for c in cards:
        a = c.select_one('a[href]')
        title = a.get_text(strip=True) if a else c.get_text(' ', strip=True)[:140]
        href = a.get('href') if a else ''
        full = urljoin('https://getmatch.ru', href)
        out.append({'date': datetime.utcnow().isoformat(), 'title': title, 'company':'', 'location':'remote', 'source':'getmatch', 'url':full, 'snippet':''})
    return out

def parse_linkedin_search(query):
    # Best-effort: public LinkedIn jobs search. For stable results add LINKEDIN_COOKIES env var as cookie header
    base = 'https://www.linkedin.com/jobs/search/?'
    params = {'keywords': query, 'location': 'Worldwide', 'f_TP': '1'}
    url = base + urlencode(params)
    headers = HEADERS.copy()
    # if user provided cookies in env var, attach
    import os
    cookies = os.getenv('LINKEDIN_COOKIES')
    if cookies:
        headers['Cookie'] = cookies
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'lxml')
    out = []
    # find job cards
    cards = soup.select('li.jobs-search-results__list-item, div.result-card, div.jobs-search__results-list li')
    for c in cards[:40]:
        t = c.select_one('h3') or c.select_one('h2') or c.select_one('a.job-card-list__title')
        comp = c.select_one('h4') or c.select_one('a.job-card-container__company-name') or c.select_one('.result-card__subtitle')
        loc = c.select_one('.job-result-card__location') or c.select_one('.result-card__meta') or c.select_one('.job-card-container__metadata-item')
        link = c.select_one('a') and c.select_one('a').get('href')
        title = t.get_text(strip=True) if t else ''
        company = comp.get_text(strip=True) if comp else ''
        location = loc.get_text(strip=True) if loc else ''
        snippet = c.get_text(' ', strip=True)[:400]
        out.append({'date': datetime.utcnow().isoformat(), 'title': title, 'company': company, 'location': location, 'source': 'linkedin', 'url': link, 'snippet': snippet})
    return out
