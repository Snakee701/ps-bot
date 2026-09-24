import os
import random
import threading
import time
import requests
import re
from flask import Flask
import discord
from discord.ext import tasks
from deep_translator import GoogleTranslator, LingvaTranslator, MyMemoryTranslator

# --- سيرفر وهمي يبقي البوت متصلاً ---
app = Flask('')

@app.route('/')
def home():
    return "PlayStation Archive Bot is Alive and Running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

def self_ping():
    """دالة تصحي السيرفر كل 4 دقائق تلقائياً لمنع خمول Render"""
    time.sleep(10)
    url = "https://ps-bot-fq0t.onrender.com"
    while True:
        try:
            requests.get(url, timeout=10)
            print("🔄 Self-ping sent successfully!")
        except Exception as e:
            print(f"⚠️ Self-ping error: {e}")
        time.sleep(240)

# --- المتغيرات الأساسية ---
TOKEN = os.getenv('BOT_TOKEN')
RAWG_API_KEY = os.getenv('RAWG_API_KEY')
CHANNEL_ID = 1392242746718162997

# 27 = PlayStation 1 | 15 = PlayStation 2
PLATFORMS = "27,15"

COLOR_PALETTE = [
    0x8B0000, 0x00439C, 0x2E8B57, 0x4B0082, 
    0xD4AF37, 0xFF4500, 0x2F4F4F, 0x1C1C1C
]

HEADER_STYLES = [
    "🏛️ أرشيف الألعاب الكلاسيكية • CLASSIC ARCHIVE",
    "🎮 جوهرة من ألعاب الزمن الجميل • RETRO GEM",
    "📜 سجلات بلايستيشن الخالدة • PLAYSTATION LEGENDS",
    "🕹️ استرجاع ذكريات الـ PlayStation • MEMORIES",
    "🔥 تحفة فنية من الجيل الذهبي • GOLDEN ERA"
]

AUTHOR_ICONS = [
    "https://cdn.discordapp.com/attachments/1382017672253800479/1552255596902744074/1.jpg"
]

THUMBNAIL_ICONS = [
    "https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/PlayStation_logo.svg/1024px-PlayStation_logo.svg.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Playstation_logo_colour.svg/1024px-Playstation_logo_colour.svg.png"
]

FOOTER_TEXTS = [
    "PLAYSTATION ARCHIVE • الذكريات لا تُمحى من الذاكرة",
    "GOLDEN ERA SYSTEM • من عصر العمالقة والجيل الذهبي",
    "CLASSIC RETRO BOT • أرشيف البلايستيشن التلقائي"
]

TITLE_DECORATIONS = [
    ("━━━ 🎮 ", " ━━━"),
    ("❖ ━━━━ [ ", " ] ━━━━ ❖"),
    ("⚔️ ─── ", " ─── ⚔️")
]

DIVIDERS = [
    "──────────────────────────────",
    "══════════════════════════════",
    "❖ ─── ✦ ─── ❖ ─── ✦ ─── ❖",
    "------------------------------"
]

GENRES_TRANSLATION = {
    "Action": "أكشن",
    "Adventure": "مغامرات",
    "Shooter": "تصويب / شوتر",
    "RPG": "أدوار / آر بي جي",
    "Role-Playing Games (RPG)": "أدوار / آر بي جي",
    "Strategy": "إستراتيجية",
    "Puzzle": "ألغاز",
    "Racing": "سباقات",
    "Sports": "رياضة",
    "Fighting": "قتال",
    "Simulation": "محاكاة",
    "Arcade": "آركيد",
    "Platformer": "منصات / بلاتفورمر",
    "Massively Multiplayer": "جماعية ضخمة",
    "Family": "عائلية",
    "Educational": "تعليمية",
    "Card": "بطاقات / كروت",
    "Casual": "خفيفة / كاجوال"
}

def clean_text(text):
    """تنظيف النص وإزالة أوسام HTML والأكواد الغريبة"""
    if not text:
        return ""
    clean = re.sub(r'<[^>]+>', '', text)
    clean = re.sub(r"'''[^']*'''", '', clean)
    clean = re.sub(r'https?://\S+', '', clean)
    clean = " ".join(clean.split())
    return clean

def translate_description(text, game_title="", genres=[]):
    """نظام ترجمة محصّن يجرب عدة محركات متطورة للترجمة الفعلية"""
    cleaned = clean_text(text)
    if not cleaned:
        return f"تعتبر لعبة {game_title} من العناوين الشيقة الكلاسيكية التي قدمت تجربة ألعاب مميزة على أجهزة البلايستيشن."

    # تقليل النص إلى 250 حرف فقط لضمان سرعة واستجابة الترجمة ومنع الحظر
    short_text = cleaned[:250]

    # 1. محاولة Google عبر deep-translator
    try:
        translated = GoogleTranslator(source='auto', target='ar').translate(short_text)
        if translated and len(translated.strip()) > 10:
            return translated.strip() + "..."
    except Exception as e:
        print(f"Deep Google Error: {e}")

    # 2. محاولة Lingva عبر deep-translator
    try:
        translated = LingvaTranslator(source='en', target='ar').translate(short_text)
        if translated and len(translated.strip()) > 10:
            return translated.strip() + "..."
    except Exception as e:
        print(f"Deep Lingva Error: {e}")

    # 3. محاولة MyMemory عبر deep-translator
    try:
        translated = MyMemoryTranslator(source='en-US', target='ar-SA').translate(short_text)
        if translated and "MYMEMORY" not in translated and len(translated.strip()) > 10:
            return translated.strip() + "..."
    except Exception as e:
        print(f"Deep MyMemory Error: {e}")

    # 4. محاولة طلب مباشر لسيرفر ترجمة آخر (Apertium/MyMemory Direct)
    try:
        url = f"https://api.mymemory.translated.net/get?q={requests.utils.quote(short_text)}&langpair=en|ar"
        res = requests.get(url, timeout=4)
        if res.status_code == 200:
            trans = res.json().get("responseData", {}).get("translatedText", "")
            if trans and "MYMEMORY" not in trans and len(trans) > 10:
                return trans + "..."
    except Exception:
        pass

    # 5. في حال حظر جميع السيرفرات تماماً، يقوم البوت بتركيب نبذة ديناميكية تتغير حسب اللعبة وتصنيفها
    genre_name = genres[0] if genres else "المغامرات والأكشن"
    return f"تعتبر **{game_title}** واحدة من أبرز ألعاب فئة ({genre_name}) التي صدرت في العصر الذهبي للبلايستيشن، وتقدم أسلوب لعب ممتع وتجربة كلاسيكية لا تُنسى."

def generate_rating_bar(rating):
    """إنشاء شريط تقييم بصري مجسم"""
    try:
        score = float(rating)
        filled = int(round((score / 5.0) * 10))
        filled = max(0, min(10, filled))
        bar = "▰" * filled + "▱" * (10 - filled)
        return f"`[{bar}]` **{score:.1f} / 5.0**"
    except (ValueError, TypeError):
        return "`[▱▱▱▱▱▱▱▱▱▱]` **N/A**"

def get_badge(rating, released_year):
    """تحديد الشارة التفاعلية بناءً على التقييم وسنة الإصدار"""
    try:
        score = float(rating)
        if score >= 4.2:
            return "🏆 **تحفة أسطورية • MUST PLAY**"
        elif score >= 3.5:
            return "💎 **كلاسيكية نادرة • RETRO GEM**"
    except (ValueError, TypeError):
        pass

    if released_year and str(released_year).isdigit() and int(released_year) < 2000:
        return "⌛ **أرشيف التسعينات • 90s CLASSIC**"
    
    return "🎮 **لعبة كلاسيكية • RETRO GAME**"

def fetch_random_game():
    """جلب لعبة عشوائية حصرية لمنصات PS1 و PS2"""
    try:
        page_num = random.randint(1, 40)
        url = f"https://api.rawg.io/api/games?key={RAWG_API_KEY}&platforms={PLATFORMS}&page={page_num}&page_size=20"
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            games = response.json().get('results', [])
            if games:
                game = random.choice(games)
                detail_url = f"https://api.rawg.io/api/games/{game['id']}?key={RAWG_API_KEY}"
                detail_resp = requests.get(detail_url, timeout=10).json()
                return detail_resp
    except Exception as e:
        print(f"خطأ أثناء جلب البيانات: {e}")
    return None

def build_game_embed(game):
    """بناء البطاقة وتصفية البيانات وإضافة العناصر البصرية"""
    title = game.get('name', 'لعبة غير معروفة')
    game_image = game.get('background_image', '')
    released = game.get('released', 'غير معروف')
    released_year = released.split('-')[0] if released and '-' in released else ''
    rating = game.get('rating', 'N/A')
    
    # تصفية أجهزة البلايستيشن
    all_platforms = [p['platform']['name'] for p in game.get('platforms', [])]
    ps_platforms = [p for p in all_platforms if "PlayStation" in p or "PS" in p]
    platforms_str = ", ".join(ps_platforms) if ps_platforms else "PlayStation 1 / 2"
    
    # المطورين
    raw_devs = [d['name'] for d in game.get('developers', [])]
    clean_devs = [clean_text(d) for d in raw_devs if not d.startswith("'''")]
    developers = ", ".join(filter(None, clean_devs)) or "غير معروف"
    
    # التصنيف
    raw_genres = [g['name'] for g in game.get('genres', [])]
    translated_genres = [GENRES_TRANSLATION.get(g, g) for g in raw_genres]
    genres_str = ", ".join(translated_genres) or "متنوع"
    
    # النبذة المترجمة ووقت القراءة
    raw_desc = game.get('description_raw') or game.get('description') or ''
    game_desc = translate_description(raw_desc, game_title=title, genres=translated_genres)
    read_time = max(1, len(game_desc) // 200)

    # العناصر الجمالية البصرية
    selected_color = random.choice(COLOR_PALETTE)
    selected_header = random.choice(HEADER_STYLES)
    selected_icon = random.choice(AUTHOR_ICONS)
    selected_thumbnail = random.choice(THUMBNAIL_ICONS)
    selected_footer = random.choice(FOOTER_TEXTS)
    divider = random.choice(DIVIDERS)
    prefix, suffix = random.choice(TITLE_DECORATIONS)
    
    badge = get_badge(rating, released_year)
    rating_bar = generate_rating_bar(rating)

    embed = discord.Embed(
        title=f"{prefix}{title.upper()}{suffix}",
        description=f"{badge}\n{divider}\n📖 **نبذة عن اللعبة:**\n{game_desc}\n\n{divider}",
        color=selected_color
    )
    
    embed.set_author(name=selected_header, icon_url=selected_icon)
    embed.set_thumbnail(url=selected_thumbnail)
    
    embed.add_field(name="🕹️ المنصات", value=f"`{platforms_str}`", inline=True)
    embed.add_field(name="🎬 المطور", value=f"`{developers}`", inline=True)
    embed.add_field(name="🏷️ التصنيف", value=f"`{genres_str}`", inline=True)
    embed.add_field(name="📅 سنة الإصدار", value=f"`{released}`", inline=True)
    embed.add_field(name="⏱️ وقت القراءة", value=f"`{read_time} دقيقة`", inline=True)
    embed.add_field(name="⭐ التقييم العام", valuerating_bar, inline=False)
    
    if game_image:
        embed.set_image(url=game_image)
        
    embed.set_footer(text=selected_footer)
    return embed

# --- كود التشغيل ---
intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ البوت متصل باسم: {client.user}')
    
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        game_data = fetch_random_game()
        if game_data:
            embed = build_game_embed(game_data)
            await channel.send(embed=embed)
            
    if not send_hourly_game.is_running():
        send_hourly_game.start()

# إرسال بطاقة لعبة جديدة كل 5 دقائق
@tasks.loop(minutes=5)
async def send_hourly_game():
    try:
        channel = client.get_channel(CHANNEL_ID)
        if channel:
            game_data = fetch_random_game()
            if game_data:
                embed = build_game_embed(game_data)
                await channel.send(embed=embed)
    except Exception as e:
        print(f"⚠️ حدث خطأ وتجاوزه البوت: {e}")

@send_hourly_game.before_loop
async def before_send_hourly_game():
    await client.wait_until_ready()

# تشغيل خادم Flask وتفعيل آلية Self-Ping للعمل 24/7
keep_alive()

ping_thread = threading.Thread(target=self_ping)
ping_thread.daemon = True
ping_thread.start()

client.run(TOKEN)
