
import os
import logging
import asyncio
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError
from yt_dlp import YoutubeDL
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Konfiguratsiya
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME') # Masalan: @xituzbekmusic

# Loglashni sozlash
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def find_and_post_music():
    if not BOT_TOKEN or not CHANNEL_USERNAME:
        logger.error("BOT_TOKEN yoki CHANNEL_USERNAME o'rnatilmagan. Bot ishga tushmaydi.")
        return

    bot = Bot(token=BOT_TOKEN)
    logger.info("Musiqa qidirish va joylash jarayoni boshlandi...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloads/%(title)s.%(ext)s', # Yuklab olingan fayllar uchun joy
        'noplaylist': True,
        'default_search': 'ytsearch',
        'max_downloads': 1,
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True, # Faqat ma'lumotlarni olish, yuklab olmaslik
    }

    try:
        # Yangi o'zbek xit qo'shiqlarini qidirish
        search_query = "yangi o'zbek xit qo'shiqlar"
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)
            if 'entries' in info and info['entries']:
                # Eng birinchi natijani olamiz
                video_info = info['entries'][0]
                video_url = video_info.get('url') or video_info.get('webpage_url')
                title = video_info.get('title', 'Noma\'lum qo\'shiq')
                artist = "Noma\'lum ijrochi"

                # Ijrochi va qo'shiq nomini ajratishga harakat qilish
                if ' - ' in title:
                    parts = title.split(' - ', 1)
                    artist = parts[0].strip()
                    title = parts[1].strip()
                elif ' by ' in title:
                    parts = title.split(' by ', 1)
                    title = parts[0].strip()
                    artist = parts[1].strip()

                logger.info(f"Topildi: {artist} - {title} ({video_url})")

                # Audio faylni yuklab olish
                download_path = f"downloads/{artist} - {title}.mp3"
                ydl_opts_download = ydl_opts.copy()
                ydl_opts_download['outtmpl'] = download_path
                ydl_opts_download['extract_flat'] = False # Yuklab olish uchun False

                with YoutubeDL(ydl_opts_download) as ydl_download:
                    ydl_download.download([video_url])
                
                if os.path.exists(download_path):
                    # Post matnini tayyorlash (Variant 1 - Oddiy)
                    post_text = (
                        f"**{artist} - {title}**\n\n"
                        f"Yangi xit taronasi! Tinglang va baho bering.\n\n"
                        f"#UzbekMusic #XitMuzika #YangiQo\'shiq\n"
                        f"Kanalga obuna bo\'ling: {CHANNEL_USERNAME}"
                    )

                    # Audio faylni kanalga yuborish
                    with open(download_path, 'rb') as audio_file:
                        await bot.send_audio(
                            chat_id=CHANNEL_USERNAME,
                            audio=audio_file,
                            caption=post_text,
                            parse_mode='Markdown'
                        )
                    logger.info(f"'{artist} - {title}' qo'shig'i kanalga joylandi.")
                    os.remove(download_path) # Faylni o'chirish
                else:
                    logger.error(f"Audio fayl yuklab olinmadi: {download_path}")
            else:
                logger.warning("Hech qanday musiqa topilmadi.")

    except TelegramError as e:
        logger.error(f"Telegram xatosi: {e}")
    except Exception as e:
        logger.error(f"Kutilmagan xato yuz berdi: {e}")
    finally:
        # Yuklab olingan fayllarni tozalash
        if os.path.exists('downloads'):
            for f in os.listdir('downloads'):
                os.remove(os.path.join('downloads', f))
            os.rmdir('downloads')

async def main():
    # 'downloads' papkasini yaratish
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    scheduler = AsyncIOScheduler()
    # Har 8 soatda ishga tushirish (kuniga 3 marta)
    scheduler.add_job(find_and_post_music, 'interval', hours=8)
    scheduler.start()
    logger.info("Bot ishga tushdi va rejalashtiruvchi faol.")

    # Botni doimiy ishlashini ta'minlash
    while True:
        await asyncio.sleep(3600) # Har soatda tekshirish

if __name__ == '__main__':
    asyncio.run(main())
