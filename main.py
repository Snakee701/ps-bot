import os
import random
import threading
import requests
import re
from flask import Flask
import discord
from discord.ext import tasks
from deep_translator import GoogleTranslator

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

def fetch_random_game():
    """جلب لعبة عشوائية حصرية لمنصات PS1 و PS2"""
    try:
        page_num = random.randint(1, 50)
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

def clean_text(text):
    """تنظيف النص وإزالة أوسام HTML والأسطر الزائدة"""
    if not text:
        return ""
    clean = re.sub(r'<[^>]+>', '', text)
    clean = " ".join(clean.split())
    return clean

def translate_to_arabic(text):
    """ترجمة موثوقة ومباشرة باستخدام deep_translator"""
    cleaned = clean_text(text)
    if not cleaned or len(cleaned) < 5:
        return "واحدة من ألعاب البلايستيشن الكلاسيكية المميزة من العصر الذهبي."

    # تقليم النص إلى 150 حرف للحصول على نبذة مركزة ومختصرة
    short_text = cleaned[:150]

    try:
        translated = GoogleTranslator(source='auto', target='ar').translate(short_text)
        if translated:
            return translated + "..."
    except Exception as e:
        print(f"خطأ في مكتبة الترجمة: {e}")

    return "لعبة كلاسيكية شهيرة أُصدرت لأجهزة البلايستيشن الكلاسيكية."

def build_game_embed(game):
    """بناء البطاقة بصورة مضمونة ونبذة مترجمة بالعربي"""
    title = game.get('name', 'لعبة غير معروفة')
    game_image = game.get('background_image', '')
    released = game.get('released', 'غير معروف')
    rating = game.get('rating', 'N/A')
    
    all_platforms = [p['platform']['name'] for p in game.get('platforms', [])]
    ps_platforms = [p for p in all_platforms if "PlayStation" in p or "PS" in p]
    platforms_str = ", ".join(ps_platforms) if ps_platforms else "PlayStation 1 / 2"
    
    developers = ", ".join([d['name'] for d in game.get('developers', [])]) or "غير معروف"
    genres = ", ".join([g['name'] for g in game.get('genres', [])]) or "متنوع"
    
    raw_desc = game.get('description_raw') or game.get('description') or ''
    translated_desc = translate_to_arabic(raw_desc)

    selected_color = random.choice(COLOR_PALETTE)
    selected_header = random.choice(HEADER_STYLES)
    selected_icon = random.choice(AUTHOR_ICONS)
    selected_footer = random.choice(FOOTER_TEXTS)
    prefix, suffix = random.choice(TITLE_DECORATIONS)

    embed = discord.Embed(
        title=f"{prefix}{title.upper()}{suffix}",
        description=f"📖 **نبذة مختصرة:**\n{translated_desc}\n\n──────────────────────────────",
        color=selected_color
    )
    
    embed.set_author(name=selected_header, icon_url=selected_icon)
    
    embed.add_field(name="🕹️ المنصات", value=f"`{platforms_str}`", inline=True)
    embed.add_field(name="🎬 المطور", value=f"`{developers}`", inline=True)
    embed.add_field(name="🏷️ التصنيف", value=f"`{genres}`", inline=True)
    embed.add_field(name="📅 سنة الإصدار", value=f"`{released}`", inline=True)
    embed.add_field(name="⭐ التقييم العام", value=f"**{rating} / 5** 🌟", inline=True)
    
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
