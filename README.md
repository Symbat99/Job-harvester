# Job Harvester — macOS
Проект собирает вакансии по ролям **Commercial / Revenue Analyst, Growth Analyst, Partner Performance Analyst** из LinkedIn (best-effort), публичных Telegram-каналов и сайта GetMatch (remote фильтр).Собирает, фильтрует по ключевым словам, сохраняет CSV, отправляет оповещения в Telegram и Email.

### Что делает
- парсит `https://www.linkedin.com/jobs/search/...` (best-effort, может требовать cookies)
- парсит публичные каналы: https://t.me/s/foranalysts, /geekjobs, /remotegeekjob, /zarubezhom_jobs
- парсит GetMatch: https://getmatch.ru/vacancies?p=1&sa=150000&l=remote&pa=all
- объединяет результаты, дедуплицирует по URL, сохраняет `data/jobs.csv`
- отправляет уведомление в Telegram бот и/или на Email
- запускается как cron job или вручную

### Быстрый старт (macOS)
1. Склонировать проект или распаковать архив.
2. Создать и активировать виртуальное окружение:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
3. Создать `.env` в корне проекта и заполнить параметры (пример ниже).
4. Запустить вручную:
```bash
python main.py
```
5. Добавить в `crontab -e` (пример запуска в 10:00 локального времени):
```
0 10 * * * /path/to/project/venv/bin/python /path/to/project/main.py >> /path/to/project/harvester.log 2>&1
```

### .env пример
```
KEYWORDS=Commercial Analyst,Growth Analyst,Partner Performance Analyst,Коммерческий аналитик,Аналитик дохода,Партнёрский аналитик
LINKEDIN_COOKIES=  # необязательно; если есть - вставь cookie header для LinkedIn
TELEGRAM_BOT_TOKEN=123456:ABC-DEF
TELEGRAM_CHAT_ID=-1001234567890
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USER=user@example.com
SMTP_PASS=secret
EMAIL_TO=you@example.com
OUTPUT_CSV=data/jobs.csv
```

### Примечания
- LinkedIn: публичный парсинг хрупок; для стабильности используй API/authorized scraping с cookies или использууй альтернативы (Indeed, Glassdoor).
- Telegram: проект парсит публичную страницу `https://t.me/s/<channel>`; если канал приватный — не будет работать.
- GetMatch: парсится HTML страницей.

Файлы в архиве:
- main.py — точка входа, scheduler
- harvester.py — основная логика сбора и агрегации
- parsers.py — парсеры по источникам
- notifier.py — Telegram/Email
- requirements.txt
- run.sh — пример запуска
