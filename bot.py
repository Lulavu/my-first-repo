import logging
import os

import feedparser
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ.get("CHAT_ID")

RSS_FEEDS = [
    "https://www.infobae.com/economia/rss.xml",
    "https://www.cronista.com/files/rss/economia.xml",
    "https://www.iprofesional.com/rss/economia.xml",
]

KEYWORDS = [
    "economía",
    "economia",
    "dólar",
    "dolar",
    "inflación",
    "inflacion",
    "finanzas",
    "inversión",
    "inversion",
    "ahorro",
    "banco",
    "mercado",
    "inteligencia artificial",
    "ia",
    "ai",
]

FOOTER = "\n💡 Cuando quieras tu lección de hoy, escribile a Claude → claude.ai"


def fetch_news(max_items: int = 5) -> list[str]:
    items = []
    seen_titles = set()

    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
        except Exception as exc:
            logger.warning("Error leyendo feed %s: %s", url, exc)
            continue

        for entry in feed.entries[:10]:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            if not title or title in seen_titles:
                continue

            text = f"{title} {entry.get('summary', '')}".lower()
            if not any(kw in text for kw in KEYWORDS):
                continue

            seen_titles.add(title)
            items.append(f"• {title}\n  {link}")

            if len(items) >= max_items:
                return items

    # Fallback: si no hay suficientes matches por keyword, completar con los más recientes
    if len(items) < 3:
        for url in RSS_FEEDS:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()
                if not title or title in seen_titles:
                    continue
                seen_titles.add(title)
                items.append(f"• {title}\n  {link}")
                if len(items) >= max_items:
                    return items

    return items


def build_message() -> str:
    news = fetch_news()
    if not news:
        body = "No se encontraron noticias relevantes hoy."
    else:
        body = "\n".join(news)

    return f"📰 Noticias del día: economía, finanzas e IA\n\n{body}\n{FOOTER}"


async def send_daily_news(application: Application) -> None:
    if not CHAT_ID:
        logger.warning("CHAT_ID no configurado, no se puede enviar el mensaje diario.")
        return
    message = build_message()
    await application.bot.send_message(chat_id=CHAT_ID, text=message, disable_web_page_preview=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        f"¡Hola! Tu chat_id es: {chat_id}\n"
        "Guardalo como variable de entorno CHAT_ID para recibir las noticias diarias a las 9am (GMT-3)."
    )


async def news_now(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(build_message(), disable_web_page_preview=True)


def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("news", news_now))

    scheduler = AsyncIOScheduler(timezone="America/Argentina/Buenos_Aires")
    scheduler.add_job(
        send_daily_news,
        trigger=CronTrigger(hour=7, minute=0),
        args=[application],
    )
    scheduler.start()

    application.run_polling()


if __name__ == "__main__":
    main()
