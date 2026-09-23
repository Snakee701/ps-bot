import os
import random
import threading
import requests
import re
import urllib.parse
from flask import Flask
import discord
from discord.ext import tasks

# --- سيرفر وهمي يبقي البوت متصلاً ---
app = Flask('')

@app.route('/')
def home():
    return "PlayStation Archive Bot is Running!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

# --- المتغيرات الأساسية ---
TOKEN = os.getenv('BOT_TOKEN')
RAWG_API_KEY = os.getenv('RAWG_API_KEY')
CHANNEL_ID = 1392242746718162997

PLATFORMS = "15,16"  # منصات PS2 (15) و PS3 (16)

# --- قائمة الألوان الأسطورية الشاملة (Hex Colors) ---
COLOR_PALETTE = [
    0x8B0000, # أحمر داكن عتيق (Resident Evil / DMC)
    0x00439C, # أزرق بلايستيشن كلاسيكي (PlayStation Blue)
    0x2E8B57, # أخضر عسكري (Metal Gear Solid)
    0x4B0082, # بنفسجي غامق غامض (Silent Hill)
    0xD4AF37, # ذهبي فاخر (God of War)
    0xFF4500, # برتقالي ناري (GTA / Action)
    0x2F4F4F, # رمادي زيتي داكن (Dark Fantasy)
    0x1C1C1C, # أسود كلاسيكي فاخر (Black Edition)
    0x708090, # فضي معدني (Cybernetic)
    0x800000, # عنابي داكن (Classic Horror)
    0x008080, # تركوازي داكن (Retro Arcade)
    0xDAA520, # برونزي عتيق (Classic Treasures)
    0x8A2BE2, # بنفسجي نيون (Neon Retro)
    0x00CED1, # أزرق سماوي مشع
]

# --- عناوين بطاقات عشوائية ومتنوعة ---
HEADER_STYLES = [
    "🏛️ أرشيف الألعاب الكلاسيكية • CLASSIC ARCHIVE",
    "🎮 جوهرة من ألعاب الزمن الجميل • RETRO GEM",
    "📜 سجلات بلايستيشن الخالدة • PLAYSTATION LEGENDS",
    "🕹️ استرجاع ذكريات الـ PlayStation • MEMORIES",
    "🔥 تحفة فنية من الجيل الذهبي • GOLDEN ERA",
    "📼 من طيات التاريخ والذكريات • NOSTALGIA",
    "⚔️ أسطورة من أساطير PS2 & PS3 • LEGENDARY GAME",
    "💿 من ذاكرة البلايستيشن الخالدة • DISC ARCHIVE",
]

# --- أيقونات عشوائية أعلى البطاقة ---
AUTHOR_ICONS = [
    "https://cdn.discordapp.com/attachments/1382017672253800479/1552255596902744074/1.jpg",
    "https://images.rawg.io/media/games/20a/20aa27a2c317978d11864143d1a836d3.jpg",
    "https://images.rawg.io/media/games/d1a/d1a2e99ade53494c69e51e0074cf2113.jpg",
]

# --- عبارات ختامية عشوائية وحماسية (Footers) ---
FOOTER_TEXTS = [
    "PLAYSTATION ARCHIVE • الذكريات لا تُمحى من الذاكرة",
    "GOLDEN ERA SYSTEM • من عصر العمالقة والجيل الذهبي",
    "CLASSIC RETRO BOT • أرشيف البلايستيشن التلقائي",
    "PS2 & PS3 VAULT • تحف وأساطير عالم الألعاب",
    "LEGENDS NEVER DIE • ألعاب حُفرت في الوجدان",
]

# --- زخارف وأشكال تحيط بالـ Title ---
TITLE_DECORATIONS = [
    ("━━━ 🎮 ", " ━━━"),
    ("❖ ━━━━ [ ", " ] ━━━━ ❖"),
    ("⚔️ ─── ", " ─── ⚔️"),
    ("◄▒▒▒▒▒▒ ", " ▒▒▒▒▒▒►"),
    ("✦ ════━ ", " ━════ ✦"),
]

def fetch_random_game():
    """جلب لعبة عشوائية لمنصات PS2 أو PS3"""
    try:
        page_num = random.randint(1, 100)
        url = f"https://api.rawg.io/api/games?key={RAWG_API_KEY}&platforms={PLATFORMS}&page={page_num}&page_size=20"
        
        response = requests.get(url)
        if response.status_code == 200:
            games = response.json().get('results', [])
            if games:
                game = random.choice(games)
                detail_url = f"https://api.rawg.io/api/games/{game['id']}?key={RAWG_API_KEY}"
                detail_resp = requests.get(detail_url).json()
                return detail_resp
    except Exception as e:
        print(f"خطأ أثناء جلب البيانات: {e}")
    return None

def clean_html(text):
    """تنظيف وتصفية النصوص من أوسمة HTML والرموز التعبيرية المعقدة"""
    if not text:
        return ""
    clean = re.sub(r'<[^>]+>', '', text)
    clean = clean.replace('\r', ' ').replace('\n', ' ')
    return clean.strip()

def translate_to_arabic(text):
    """ترجمة النص للغة العربية عبر API جوجل المباشر والمضمون"""
    cleaned_text = clean_html(text)
    if not cleaned_text or len(cleaned_text) < 5:
        return "لا يوجد وصف متاح لهذه اللعبة حالياً في الأرشيف."
    
    try:
        short_text = cleaned_text[:300]
        encoded_text = urllib.parse.quote(short_text)
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=ar&dt=t&q={encoded_text}"
        
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            result = response.json()
            translated_sentences = [item[0] for item in result[0] if item[0]]
            translated_text = "".join(translated_sentences)
            if translated_text:
                return translated_text
    except Exception as e:
        print(f"خطأ في الترجمة: {e}")
    
    return cleaned_text

def build_game_embed(game):
    """بناء البطاقة وتطبيق العشوائية الفائقة في التصاميم والتنسيقات"""
    title = game.get('name', 'لعبة غير معروفة')
    background_image = game.get('background_image', '')
    released = game.get('released', 'غير معروف')
    rating = game.get('rating', 'N/A')
    
    # تصفية المنصات المخصصة للبلايستيشن فقط
    all_platforms = [p['platform']['name'] for p in game.get('platforms', [])]
    ps_platforms = [p for p in all_platforms if "PlayStation" in p or "PS" in p]
    platforms_str = ", ".join(ps_platforms) if ps_platforms else ", ".join(all_platforms)
    
    developers = ", ".join([d['name'] for d in game.get('developers', [])]) or "غير معروف"
    genres = ", ".join([g['name'] for g in game.get('genres', [])]) or "متنوع"
    
    # جلب الوصف وترجمته
    raw_desc = game.get('description_raw') or game.get('description') or 'لا يوجد وصف متاح.'
    translated_desc = translate_to_arabic(raw_desc)

    # اختيار عناصر التنسيق العشوائي
    selected_color = random.choice(COLOR_PALETTE)
    selected_header = random.choice(HEADER_STYLES)
    selected_icon = random.choice(AUTHOR_ICONS)
    selected_footer = random.choice(FOOTER_TEXTS)
    prefix, suffix = random.choice(TITLE_DECORATIONS)

    # إنشاء بطاقة Embed
    embed = discord.Embed(
        title=f"{prefix}{title.upper()}{suffix}",
        description=f"📖 **نبذة عن اللعبة:**\n```{translated_desc}```\n──────────────────────────────",
        color=selected_color
    )
    
    embed.set_author(name=selected_header, icon_url=selected_icon)
    
    embed.add_field(name="🕹️ المنصات", value=f"`{platforms_str}`", inline=True)
    embed.add_field(name="🎬 المطور", value=f"`{developers}`", inline=True)
    embed.add_field(name="🏷️ التصنيف", value=f"`{genres}`", inline=True)
    embed.add_field(name="📅 سنة الإصدار", value=f"`{released}`", inline=True)
    embed.add_field(name="⭐ التقييم العام", value=f"**{rating} / 5** 🌟", inline=True)
    
    if background_image:
        embed.set_image(url=background_image)
        
    embed.set_footer(text=selected_footer)
    return embed

# --- كود التشغيل الرئيسي للبوت ---
intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ البوت الأسطوري جاهز ومتصل باسم: {client.user}')
    
    # إرسال تجريبي فور التشغيل لاختبار الترجمة والتصميم
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        print("⏳ جاري إرسال بطاقة تجريبية فورية...")
        game_data = fetch_random_game()
        if game_data:
            embed = build_game_embed(game_data)
            await channel.send(embed=embed)
            print("✅ تم الإرسال التجريبي بنجاح!")
            
    if not send_hourly_game.is_running():
        send_hourly_game.start()

# --- حلقة إرسال اللعبة كل ساعة تلقائياً ---
@tasks.loop(hours=1)
async def send_hourly_game():
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        game_data = fetch_random_game()
        if game_data:
            embed = build_game_embed(game_data)
            await channel.send(embed=embed)

keep_alive()
client.run(TOKEN)
