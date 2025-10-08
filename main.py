#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from harvester import harvest_once, save_csv
from notifier import notify_telegram, notify_email
from datetime import datetime

load_dotenv()

OUT_CSV = os.getenv('OUTPUT_CSV', 'data/jobs.csv')

def main():
    items = harvest_once()
    if items:
        save_csv(items, OUT_CSV)
    msg = build_message(items)
    # send notifications if configured
    if os.getenv('TELEGRAM_BOT_TOKEN') and os.getenv('TELEGRAM_CHAT_ID'):
        notify_telegram(msg)
    if os.getenv('SMTP_SERVER') and os.getenv('EMAIL_TO'):
        notify_email(f'JobHarvester: {len(items)} new', msg)

def build_message(items):
    if not items:
        return f'JobHarvester: no new items at {datetime.utcnow().isoformat()}'
    lines = []
    for i, it in enumerate(items[:30], 1):
        lines.append(f"{i}. {it.get('title','')} — {it.get('company','')} | {it.get('location','')}\n{it.get('url','')}\n")
    return "\n".join(lines)

if __name__ == '__main__':
    main()
