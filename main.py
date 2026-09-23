import os
import random
import threading
import requests
from flask import Flask
import discord
from discord.ext import tasks

# سيرفر وهمي ليبقي البوت متصلاً في Render
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
RAWG_API_KEY = os.getenv('RAWG_API_KEY')  # ضع المفتاح في Environment Variables بـ Render
CHANNEL_ID = 1392242746718162997  # آيدي القناة

# معرفات المنصات في RAWG (15 = PS2, 16 = PS3)
PLATFORMS = "15,16" 

def fetch_random_game():
    """جلب لعبة عشوائية لمنصات PS2 أو PS3"""
    try:
        # جلب صفحة عشوائية من الألعاب (بين الصفحة 1 و 100)
        page_num = random.randint(1, 100)
        url = f"https://api.rawg.io/api/games?key={RAWG_API_KEY}&platforms={PLATFORMS}&page={page_num}&page_size=20"
        
        response = requests.get(url)
        if response.status_code == 200:
            games = response.json().get('results', [])
            if games:
                game = random.choice(games)
                # جلب تفاصيل أعمق للعبة
                detail_url = f"https://api.rawg.io/api/games/{game['id']}?key={RAWG_API_KEY}"
                detail_resp = requests.get(detail_url).json()
                return detail_resp
    except Exception as e:
        print(f"خطأ أثناء جلب البيانات: {e}")
    return None

def build_game_embed(game):
    """تصميم بطاقة ديسكورد الأنيقة تلقائياً"""
    title = game.get('name', 'لعبة غير معروفة')
    background_image = game.get('background_image', '')
    released = game.get('released', 'غير معروف')
    rating = game.get('rating', 'N/A')
    
    # جلب المنصات والمطورين
    platforms = ", ".join([p['platform']['name'] for p in game.get('platforms', [])])
    developers = ", ".join([d['name'] for d in game.get('developers', [])]) or "غير معروف"
    
    # اقتطاع الوصف إذا كان طويلاً جداً
    description = game.get('description_raw', 'لا يوجد وصف متاح لهذه اللعبة.')
    if len(description) > 300:
        description = description[:300] + "..."

    embed = discord.Embed(
        title=f"━━━ 🎮 {title.upper()} ━━━",
        description=f"📖 **نبذة عن اللعبة:**\n{description}\n\n───────────────",
        color=3447003 # لون أزرق كلاسيكي
    )
    
    embed.set_author(name="PlayStation Archive Auto-System", icon_url="https://cdn.discordapp.com/attachments/1382017672253800479/1552255596902744074/1.jpg")
    
    embed.add_field(name="🕹️ المنصات", value=platforms, inline=True)
    embed.add_field(name="🎬 المطور", value=developers, inline=True)
    embed.add_field(name="📅 تاريخ الإصدار", value=released, inline=True)
    embed.add_field(name="⭐ التقييم", value=f"{rating} / 5", inline=True)
    
    if background_image:
        embed.set_image(url=background_image)
        
    embed.set_footer(text="AUTO GAME ARCHIVE • PLAYSTATION 2 & 3")
    return embed

# --- كود الديسكورد ---
intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'البوت الذكي متصل باسم: {client.user}')
    if not send_daily_game.is_running():
        send_daily_game.start()

@tasks.loop(hours=24)
async def send_daily_game():
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        game_data = fetch_random_game()
        if game_data:
            embed = build_game_embed(game_data)
            await channel.send(embed=embed)

keep_alive()
client.run(TOKEN)
