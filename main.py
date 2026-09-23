import os
import random
import threading
import requests
from flask import Flask
import discord
from discord.ext import tasks
from deep_translator import GoogleTranslator

# سيرفر وهمي يبقي البوت متصلاً
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

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

PLATFORMS = "15,16" # PS2 و PS3

# قائمة ألوان كلاسيكية تتغير عشوائياً لكل بطاقة
COLOR_PALETTE = [
    0x990000, # أحمر داكن (DMC / Resident Evil)
    0x2b5b84, # أزرق سوني كلاسيكي
    0x4a5d23, # أخضر عسكري (Metal Gear Solid)
    0x5a3d75, # بنفسجي غامق (Silent Hill / Dark)
    0xcb9b51, # ذهبي / برونزي
    0x333333, # رمادي كلاسيكي
]

# عناوين متغيرة تعطي تنوع للبطاقات
HEADER_STYLES = [
    "🏛️ أرشيف الألعاب الكلاسيكية",
    "🎮 جوهرة من ألعاب الزمن الجميل",
    "📜 سجلات بلايستيشن الخالدة",
    "🕹️ استرجاع ذكريات الـ PlayStation",
]

def fetch_random_game():
    """جلب لعبة عشوائية لمنصات PS2 أو PS3"""
    try:
        page_num = random.randint(1, 80)
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

def translate_to_arabic(text):
    """ترجمة النص التلقائية للغة العربية"""
    if not text or text == "لا يوجد وصف متاح لهذه اللعبة.":
        return "لا يوجد وصف متاح بهذه اللعبة حالياً."
    try:
        translated = GoogleTranslator(source='auto', target='ar').translate(text)
        return translated
    except Exception:
        return text # في حال تعثرت الترجمة يرجع النص الأصلي

def build_game_embed(game):
    """تصميم بطاقة ديسكورد الأنيقة والـ Dynamic"""
    title = game.get('name', 'لعبة غير معروفة')
    background_image = game.get('background_image', '')
    released = game.get('released', 'غير معروف')
    rating = game.get('rating', 'N/A')
    
    # تصفية المنصات المخصصة للبلايستيشن فقط
    all_platforms = [p['platform']['name'] for p in game.get('platforms', [])]
    ps_platforms = [p for p in all_platforms if "PlayStation" in p or "PS" in p]
    platforms_str = ", ".join(ps_platforms) if ps_platforms else ", ".join(all_platforms)
    
    developers = ", ".join([d['name'] for d in game.get('developers', [])]) or "غير معروف"
    
    # جلب الوصف واقتطاعه ليكون مناسباً للبطاقة
    raw_desc = game.get('description_raw', 'لا يوجد وصف متاح لهذه اللعبة.')
    if len(raw_desc) > 350:
        raw_desc = raw_desc[:350] + "..."
        
    # ترجمة الوصف إلى العربية
    translated_desc = translate_to_arabic(raw_desc)

    # اختيار لون وهيدر عشوائي
    selected_color = random.choice(COLOR_PALETTE)
    selected_header = random.choice(HEADER_STYLES)

    embed = discord.Embed(
        title=f"━━━ 🎮 {title.upper()} ━━━",
        description=f"💬 **نبذة عن اللعبة:**\n{translated_desc}\n\n───────────────",
        color=selected_color
    )
    
    embed.set_author(name=selected_header, icon_url="https://cdn.discordapp.com/attachments/1382017672253800479/1552255596902744074/1.jpg")
    
    embed.add_field(name="🕹️ المنصات", value=f"`{platforms_str}`", inline=True)
    embed.add_field(name="🎬 المطور", value=f"`{developers}`", inline=True)
    embed.add_field(name="📅 سنة الإصدار", value=f"`{released}`", inline=True)
    embed.add_field(name="⭐ التقييم العام", value=f"**{rating} / 5**", inline=True)
    
    if background_image:
        embed.set_image(url=background_image)
        
    embed.set_footer(text="PLAYSTATION ARCHIVE AUTO-SYSTEM • CLASSIC GAMES")
    return embed

# --- كود الديسكورد ---
intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'البوت الذكي متصل باسم: {client.user}')
    if not send_daily_game.is_running():
        send_daily_game.start()

@tasks.loop(hours=1)
async def send_daily_game():
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        game_data = fetch_random_game()
        if game_data:
            embed = build_game_embed(game_data)
            await channel.send(embed=embed)

keep_alive()
client.run(TOKEN)
