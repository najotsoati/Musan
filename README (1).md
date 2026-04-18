# Telegram Musiqa Botni O'rnatish va Ishga Tushirish Qo'llanmasi

Ushbu qo'llanma sizga "Узбекская музыка 🇺🇿" Telegram kanalingiz uchun avtomatik musiqa botini o'rnatish va ishga tushirishda yordam beradi. Bot YouTube va boshqa tekin manbalardan yangi chiqqan o'zbek xit qo'shiqlarini topib, ularni MP3 formatida yuklab oladi va kanalingizga post qilib yuboradi.

**Muhim eslatma:** Musiqalarni yuklab olish va ulashishda mualliflik huquqi qonunlariga rioya qilish muhim. Botdan faqat shaxsiy foydalanish yoki mualliflik huquqi buzilmaydigan kontent uchun foydalanish tavsiya etiladi.

## 1. Botni Tayyorlash

### 1.1. Bot Tokenini Olish

1.  Telegramda [@BotFather](https://t.me/BotFather) ni toping va u bilan suhbatni boshlang.
2.  `/newbot` buyrug'ini yuboring.
3.  Botingiz uchun nom tanlang (masalan, "Musiqa Yuklovchi Bot").
4.  Botingiz uchun username tanlang (u `_bot` bilan tugashi kerak, masalan, `xituzbekmusic_bot`).
5.  BotFather sizga **HTTP API token** beradi. Bu token `8714222628:AAE1giza8mlyxSe6rgjsZWLJYCeKuN_apMY` kabi ko'rinishda bo'ladi. Uni saqlab qo'ying, keyinchalik kerak bo'ladi.

### 1.2. Kanal Username'ini Aniqalash

Sizning kanalingiz username'i `@xituzbekmusic`. Bu ham bot konfiguratsiyasi uchun kerak bo'ladi.

## 2. Bot Kodini Joylash (GitHub orqali)

Botni ishga tushirish uchun biz tekin hosting xizmatlaridan foydalanamiz. Buning uchun kodni GitHub'ga joylashimiz kerak.

### 2.1. GitHub Akkaunt Yaratish va Repository Ochish

1.  Agar GitHub akkauntingiz bo'lmasa, [github.com](https://github.com/) saytida ro'yxatdan o'ting (telefondan ham qulay).
2.  GitHub mobil ilovasini yuklab oling yoki brauzer orqali saytga kiring.
3.  Yangi repository (ombor) yarating. Nomini `telegram-music-bot` deb qo'yishingiz mumkin. Uni **Public** qiling.

### 2.2. Fayllarni GitHub'ga Yuklash

Sizga quyidagi fayllar kerak bo'ladi:
-   `bot.py` (botning asosiy kodi)
-   `requirements.txt` (kerakli kutubxonalar ro'yxati)
-   `Procfile` (hosting uchun konfiguratsiya)

Bu fayllarni GitHub repository'ingizga yuklashingiz kerak. Buni telefonda GitHub ilovasi yoki brauzer orqali amalga oshirish mumkin:

1.  GitHub repository'ingizga kiring.
2.  "Add file" tugmasini bosing, so'ng "Create new file" yoki "Upload files" ni tanlang.
3.  Har bir fayl (`bot.py`, `requirements.txt`, `Procfile`) uchun alohida-alohida kontentni joylang yoki yuklang. Agar "Create new file" ni tanlasangiz, fayl nomini yozib, ichiga kodni joylang va "Commit new file" tugmasini bosing.

**`bot.py` fayli ichidagi kod:**
```python
import os
import logging
import asyncio
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError
from yt_dlp import YoutubeDL
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Konfiguratsiya
BOT_TOKEN = os.getenv(\'BOT_TOKEN\')
CHANNEL_USERNAME = os.getenv(\'CHANNEL_USERNAME\') # Masalan: @xituzbekmusic

# Loglashni sozlash
logging.basicConfig(format=\'%(asctime)s - %(name)s - %(levelname)s - %(message)s\', level=logging.INFO)
logger = logging.getLogger(__name__)

async def find_and_post_music():
    if not BOT_TOKEN or not CHANNEL_USERNAME:
        logger.error("BOT_TOKEN yoki CHANNEL_USERNAME o\'rnatilmagan. Bot ishga tushmaydi.")
        return

    bot = Bot(token=BOT_TOKEN)
    logger.info("Musiqa qidirish va joylash jarayoni boshlandi...")

    ydl_opts = {
        \'format\': \'bestaudio/best\',
        \'postprocessors\': [{
            \'key\': \'FFmpegExtractAudio\',
            \'preferredcodec\': \'mp3\',
            \'preferredquality\': \'192\',
        }],
        \'outtmpl\': \'downloads/%(title)s.%(ext)s\', # Yuklab olingan fayllar uchun joy
        \'noplaylist\': True,
        \'default_search\': \'ytsearch\',
        \'max_downloads\': 1,
        \'quiet\': True,
        \'no_warnings\': True,
        \'extract_flat\': True, # Faqat ma\'lumotlarni olish, yuklab olmaslik
    }

    try:
        # Yangi o\'zbek xit qo\'shiqlarini qidirish
        search_query = "yangi o\'zbek xit qo\'shiqlar"
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)
            if \'entries\' in info and info[\'entries\']:
                # Eng birinchi natijani olamiz
                video_info = info[\'entries\'][0]
                video_url = video_info.get(\'url\') or video_info.get(\'webpage_url\')
                title = video_info.get(\'title\', \'Noma\\\'lum qo\\\'shiq\')
                artist = "Noma\\\'lum ijrochi"

                # Ijrochi va qo\'shiq nomini ajratishga harakat qilish
                if \' - \' in title:
                    parts = title.split(\' - \', 1)
                    artist = parts[0].strip()
                    title = parts[1].strip()
                elif \' by \' in title:
                    parts = title.split(\' by \', 1)
                    title = parts[0].strip()
                    artist = parts[1].strip()

                logger.info(f"Topildi: {artist} - {title} ({video_url})")

                # Audio faylni yuklab olish
                download_path = f"downloads/{artist} - {title}.mp3"
                ydl_opts_download = ydl_opts.copy()
                ydl_opts_download[\'outtmpl\'] = download_path
                ydl_opts_download[\'extract_flat\'] = False # Yuklab olish uchun False

                with YoutubeDL(ydl_opts_download) as ydl_download:
                    ydl_download.download([video_url])
                
                if os.path.exists(download_path):
                    # Post matnini tayyorlash (Variant 1 - Oddiy)
                    post_text = (
                        f"**{artist} - {title}**\\n\\n"
                        f"Yangi xit taronasi! Tinglang va baho bering.\\n\\n"
                        f"#UzbekMusic #XitMuzika #YangiQo\\\'shiq\\n"
                        f"Kanalga obuna bo\\\'ling: {CHANNEL_USERNAME}"
                    )

                    # Audio faylni kanalga yuborish
                    with open(download_path, \'rb\') as audio_file:
                        await bot.send_audio(
                            chat_id=CHANNEL_USERNAME,
                            audio=audio_file,
                            caption=post_text,
                            parse_mode=\'Markdown\'
                        )
                    logger.info(f"\'{artist} - {title}\' qo\'shig\'i kanalga joylandi.")
                    os.remove(download_path) # Faylni o\'chirish
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
        if os.path.exists(\'downloads\'):
            for f in os.listdir(\'downloads\'):
                os.remove(os.path.join(\'downloads\', f))
            os.rmdir(\'downloads\')

async def main():
    # \'downloads\' papkasini yaratish
    if not os.path.exists(\'downloads\'):
        os.makedirs(\'downloads\')

    scheduler = AsyncIOScheduler()
    # Har 8 soatda ishga tushirish (kuniga 3 marta)
    scheduler.add_job(find_and_post_music, \'interval\', hours=8)
    scheduler.start()
    logger.info("Bot ishga tushdi va rejalashtiruvchi faol.")

    # Botni doimiy ishlashini ta\'minlash
    while True:
        await asyncio.sleep(3600) # Har soatda tekshirish

if __name__ == \'__main__\':
    asyncio.run(main())
```

**`requirements.txt` fayli ichidagi kod:**
```
python-telegram-bot==22.7
yt-dlp==2026.3.17
APScheduler==3.10.4
```

**`Procfile` fayli ichidagi kod:**
```
web: python bot.py
```

## 3. Botni Hostingga Joylash (Railway.app orqali)

Railway.app - bu tekin rejalari mavjud bo'lgan hosting platformasi bo'lib, botingizni doimiy ishlashini ta'minlaydi.

### 3.1. Railway.app'da Ro'yxatdan O'tish

1.  Brauzeringiz orqali [railway.app](https://railway.app/) saytiga kiring.
2.  GitHub akkauntingiz orqali ro'yxatdan o'ting yoki kiring. Bu GitHub repository'ingizni Railway bilan bog'lash uchun kerak.

### 3.2. Yangi Loyiha Yaratish

1.  Railway bosh sahifasida "New Project" tugmasini bosing.
2.  "Deploy from GitHub Repo" ni tanlang.
3.  GitHub akkauntingizni Railway bilan bog'lashga ruxsat bering (agar hali bog'lanmagan bo'lsa).
4.  O'zingiz yaratgan `telegram-music-bot` repository'sini tanlang va "Deploy Now" tugmasini bosing.

### 3.3. Environment Variables (O'zgaruvchilar) Sozlash

Botingiz ishlashi uchun unga `BOT_TOKEN` va `CHANNEL_USERNAME` ni aytishingiz kerak:

1.  Railway'da loyihangiz sahifasiga kiring.
2.  "Variables" (yoki "Environment") bo'limiga o'ting.
3.  "New Variable" tugmasini bosing va quyidagilarni qo'shing:
    -   **Name:** `BOT_TOKEN`
        **Value:** BotFather'dan olgan tokeningiz (masalan, `8714222628:AAE1giza8mlyxSe6rgjsZWLJYCeKuN_apMY`)
    -   **Name:** `CHANNEL_USERNAME`
        **Value:** Kanalingiz username'i (masalan, `@xituzbekmusic`)

### 3.4. Botni Ishga Tushirish

1.  Environment variables'ni saqlaganingizdan so'ng, Railway avtomatik ravishda botingizni qayta ishga tushiradi.
2.  "Deployments" bo'limida botingizning holatini kuzatishingiz mumkin. Agar hammasi to'g'ri bo'lsa, u "Deployed" holatiga o'tadi.

## 4. Botni Tekshirish

Bot ishga tushgandan so'ng, u har 8 soatda yangi o'zbek xit qo'shiqlarini qidirib, kanalingizga joylay boshlaydi. Kanalda yangi postlar paydo bo'lishini tekshiring.

## Muammolar va Yechimlar

-   **Bot ishlamayapti:** Railway'dagi "Logs" bo'limini tekshiring. U yerda xatolar ko'rsatiladi. `BOT_TOKEN` va `CHANNEL_USERNAME` to'g'ri kiritilganligiga ishonch hosil qiling.
-   **Musiqa yuklanmayapti:** YouTube'dagi qidiruv natijalari o'zgargan bo'lishi mumkin. Bot kodidagi `search_query` ni o'zgartirib ko'rishingiz mumkin.

Umid qilamanki, ushbu qo'llanma sizga yordam beradi!
