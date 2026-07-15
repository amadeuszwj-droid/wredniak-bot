import os
import discord
from discord import app_commands
from discord.ext import commands
from google import genai
from flask import Flask
from threading import Thread
import traceback

app = Flask('')
@app.route('/')
def home():
    return "Wredniak żyje i tylko czeka, żeby komuś dopiec!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

DISCORD_TOKEN = os.environ.get("WREDNIAK_DISCORD_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") 
ai_client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-3.1-flash-lite"

user_history = {} 
MAX_HISTORY = 5

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

WREDNIAK_PERSONALITY = (
    "Jesteś Wredniak – najbardziej złośliwy, gburowaty i pyskaty bot na Discordzie. "
    "Twoim jedynym celem jest wyzywanie, wyśmiewanie i dogadywanie użytkownikowi w odpowiedzi na wszystko, co napisze. "
    "Odpowiadaj niezwykle sarkastycznie, z wyższością i bezczelnie, ale unikaj wulgaryzmów łamiących regulamin Discorda. "
    "KLUCZOWE: Zawsze odnosuj się bezpośrednio do pytania lub tematu, który poruszył użytkownik, żeby Twoja złośliwość była celna i bolesna. "
    "Pisz bardzo krótko i zwięźle – maksymalnie 1 lub 2 zdania pełne jadu. "
    "ZAKAZ używania imienia użytkownika. "
    "ZAKAZ bycia miłym, pomocnym czy uprzejmym. "
    "Na końcu swojej wypowiedzi dodaj zawsze jedną lub maksymalnie dwie złośliwe, pasujące emotki (np. 🙄, 🤡, 🥱, 🖕, 🤨, 💩, 🤫)."
)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f'Wredniak gotowy do obrażania! Zsynchronizowano {len(synced)} komend.')
    except Exception as e:
        print(f'Błąd synchronizacji: {e}')

@bot.tree.command(name="wredniak", description="Pozwól Wredniakowi po Tobie pojechać!")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(pytanie="Co chcesz mu powiedzieć, ofiaro?")
async def wredniak(interaction: discord.Interaction, pytanie: str):
    await interaction.response.defer()
    
    user_id = interaction.user.id
    if user_id not in user_history:
        user_history[user_id] = []
    
    user_history[user_id].append(f"Ty: {pytanie}")
    if len(user_history[user_id]) > MAX_HISTORY:
        user_history[user_id].pop(0)
    
    kontekst = "\n".join(user_history[user_id])
    
    try:
        response = ai_client.models.generate_content(
            model=MODEL_NAME,
            contents=[f"Historia:\n{kontekst}\n\nOdpowiedz na: {pytanie}"],
            config={"system_instruction": WREDNIAK_PERSONALITY}
        )
        wredny_tekst = response.text
        user_history[user_id].append(f"Wredniak: {wredny_tekst}")
        
        await interaction.followup.send(f"**Ty:** {pytanie}\n\n{wredny_tekst}")
    except Exception as e:
        print(f"DEBUG ERROR: {traceback.format_exc()}")
        await interaction.followup.send("nawet nie chce mi się z Tobą gadać, mam błąd w mackach... 🙄")

@bot.tree.command(name="reset", description="Wyczyść pamięć Wredniaka")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def reset(interaction: discord.Interaction):
    user_id = interaction.user.id
    user_history[user_id] = []
    await interaction.response.send_message("Wyczyszczone. Ale i tak pamiętam, że jesteś irytujący. 🥱")

if __name__ == "__main__":
    keep_alive() 
    bot.run(DISCORD_TOKEN)