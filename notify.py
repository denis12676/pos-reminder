"""Send the current POS step to Telegram. Runs on GitHub Actions - no laptop needed.

Reads step.md from this repository. No personal data lives here.
Env: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID.
"""
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

TZ = timezone(timedelta(hours=3))
DAYS_RU = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]


def field(text, name, default=""):
    m = re.search(rf"\*\*{name}:?\*\*\s*(.+)", text)
    return m.group(1).strip() if m else default


def build_message():
    with open("step.md", encoding="utf-8") as f:
        step_file = f.read()

    step = field(step_file, "Шаг", "открыть урок")
    first = field(step_file, r"Первый шаг \(5 мин\)")
    link = field(step_file, "Ссылка", "https://lk.neural-university.ru/learning-program-v2/learn")
    streak = field(step_file, "Цепочка", "0")

    today = datetime.now(TZ).date()
    head = f"Цепочка: {streak} дн." if streak.isdigit() and int(streak) else "Старт"
    lines = [
        f"{head} · {today:%d.%m}, {DAYS_RU[today.weekday()]}",
        "",
        f"Сегодня: {step}",
        f"Первый шаг (5 мин): {first}" if first else "",
        "",
        f"→ {link}",
        "",
        "5 минут с телефона = день засчитан.",
    ]
    return "\n".join(x for x in lines if x)


def send(text):
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": "true",
    }).encode()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=30) as r:
        return r.status


if __name__ == "__main__":
    msg = build_message()
    print(msg)
    if "--dry-run" not in sys.argv:
        print("status:", send(msg))
