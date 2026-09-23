import os
import discord
from discord.ext import tasks

# يقرأ التوكن بأمان من متغيرات البيئة في Render
TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = 1552353677031776257

EMBEDS_DATABASE = [
    {
        "author": {
            "name": "PlayStation Archive By FHD_705",
            "icon_url": "https://cdn.discordapp.com/attachments/1382017672253800479/1552255596902744074/1.jpg"
        },
        "title": "━━━ 🔴 DANTE | دانتي ━━━",
        "description": "💬 **مقولة شهيرة:**\n\"Devils Never Cry... They only howl like the wind.\"\n\n📖 **نبذة عن الشخصية:**\nصائد الشياطين الهجين (نصف بشر ونصف شيطان)، ابن الفارس الأسطوري 'سباردا'. يتميز بأسلوبه الساخر أثناء القتال ومهارته الخارقة في استخدام سيف Rebellion ومسدساته الشهيرة Ebony & Ivory.\n\n───────────────",
        "color": 11141120,
        "fields": [
            {"name": "🎮 السلسلة / اللعبة", "value": "Devil May Cry Series"},
            {"name": "🎬 المطور والناشر", "value": "Capcom"},
            {"name": "🎭 السمة والشخصية", "value": "استعراضي / ساخر / قوة شياطين هجينة"},
            {"name": "🗡️ السلاح الإيقوني", "value": "سيف Rebellion • المسدسان Ebony & Ivory"}
        ],
        "footer": {"text": "CHARACTER ARCHIVE • DEVIL MAY CRY"}
    }
]

intents = discord.Intents.default()
client = discord.Client(intents=intents)
current_index = 0

@client.event
async def on_ready():
    print(f'تم تسجيل الدخول باسم: {client.user}')
    send_scheduled_embed.start()

@tasks.loop(hours=24)
async def send_scheduled_embed():
    global current_index
    channel = client.get_channel(CHANNEL_ID)
    if channel and current_index < len(EMBEDS_DATABASE):
        data = EMBEDS_DATABASE[current_index]
        embed = discord.Embed.from_dict(data)
        await channel.send(embed=embed)
        current_index += 1

client.run(TOKEN)
