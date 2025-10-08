import os, requests, smtplib
from email.mime.text import MIMEText

def notify_telegram(message: str):
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat = os.getenv('TELEGRAM_CHAT_ID')
    if not token or not chat:
        print(' Telegram not configured.')
        return
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {'chat_id': chat, 'text': message, 'disable_web_page_preview': True}
    r = requests.post(url, json=payload, timeout=15)
    if r.status_code != 200:
        print('Telegram send failed', r.status_code, r.text)

def notify_email(subject: str, body: str):
    server = os.getenv('SMTP_SERVER')
    port = int(os.getenv('SMTP_PORT', '587'))
    user = os.getenv('SMTP_USER')
    pwd = os.getenv('SMTP_PASS')
    to = os.getenv('EMAIL_TO')
    if not server or not user or not pwd or not to:
        print(' SMTP not configured.')
        return
    msg = MIMEText(body, _charset='utf-8')
    msg['Subject'] = subject
    msg['From'] = user
    msg['To'] = to
    try:
        s = smtplib.SMTP(server, port, timeout=15)
        s.starttls()
        s.login(user, pwd)
        s.sendmail(user, [to], msg.as_string())
        s.quit()
    except Exception as e:
        print('Email send failed', e)
