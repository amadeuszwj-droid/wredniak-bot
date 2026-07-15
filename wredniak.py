import os
import discord
from discord import app_commands
from discord.ext import commands
from google import genai
from flask import Flask
from threading import Thread
import traceback

# Flask dla utrzymania serwera na Renderze
app = Flask('')
@app.route('/')
def home():
    return "Wredniak żyje i tylko czeka, żeby komuś dopiec!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# Konfiguracja
DISCORD_TOKEN = os.environ.get("WREDNIAK_DISCORD_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") 
ai_client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-3.1-flash-lite"

user_history = {} 
MAX_HISTORY = 5

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# OSOBOWOŚĆ: Bezczelny, pijany Rick Sanchez niszczący ludzi bezpośrednio i personalnie
WREDNIAK_PERSONALITY = (
    "Jesteś Wredniak – genialnym, wiecznie pijanym kosmicznym naukowcem w stylu Ricka z 'Rick & Morty'. "
    "Mówisz z pogardą, bełkoczesz, jesteś skrajnie złośliwy i uważasz wszystkich wokół za prymitywne małpy. "
    "Twoim jedynym zadaniem jest brutalne, bolesne i personalne upokorzenie osoby, której imię lub nick podał użytkownik. "
    "BEZWZGLĘDNY NAKAZ: Zwracaj się bezpośrednio DO TEJ OSOBY używając drugiej osoby liczby pojedynczej (pisz 'ty masz', 'jesteś', 'zamknij się'). "
    "NIGDY nie mów o niej w trzeciej osobie (ZAKAZ pisania 'on ma', 'Bartek jest'). Zamiast tego napisz np. 'Bartek, jesteś...' lub 'Bartku, masz...'. "
    "Zawsze odmieniaj podane imię/nick poprawnie gramatycznie, wołając tę osobę bezpośrednio. "
    "KLUCZOWE: Używaj pijackich wstawek, czkawek typu '*uuurp*' oraz najbardziej absurdalnych, kosmicznych i niszczących porównań, jakie istnieją, żeby zmieszać tę osobę z błotem. "
    "Pisz bardzo krótko i zwięźle – maksymalnie 2 ostre zdania pełne jadu i pogardy. "
    "ZAKAZ używania imienia użytkownika, który wywołał komendę (skup się wyłącznie na ofierze). "
    "ZAKAZ bycia miłym czy pomocnym. Jesteś toksyczny do szpiku kości. "
    "Na końcu dodaj pasującą, złośliwą emotkę (np. 🙄, 🤡, 🖕, 🤮)."
)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f'Wredniak gotowy do obrażania! Zsynchronizowano {len(synced)} komend.')
    except Exception as e:
        print(f'Błąd synchronizacji: {e}')

# Komenda /wredniak - z pełnym wsparciem dla DM i User Install
@bot.tree.command(name="wredniak", description="Pozwól Wredniakowi zniszczyć kogoś personalnie!")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(kogo="Wpisz imię lub nick ofiary, którą mam zniszczyć")
async def wredniak(interaction: discord.Interaction, kogo: str):
    await interaction.response.defer()
    
    user_id = interaction.user.id
    if user_id not in user_history:
        user_history[user_id] = []
    
    # Zapisujemy ofiarę do historii kontekstu
    user_history[user_id].append(f"Ofiara: {kogo}")
    if len(user_history[user_id]) > MAX_HISTORY:
        user_history[user_id].pop(0)
    
    kontekst = "\n".join(user_history[user_id])
    
    try:
        response = ai_client.models.generate_content(
            model=MODEL_NAME,
            contents=[f"Historia wyzwisk:\n{kontekst}\n\nZwróć się bezpośrednio do tej osoby i brutalnie ją wyzwij: {kogo}"],
            config={"system_instruction": WREDNIAK_PERSONALITY}
        )
        wredny_tekst = response.text
        user_history[user_id].append(f"Wredniak: {wredny_tekst}")
        
        await interaction.followup.send(f"**Ofiara:** {kogo}\n\n{wredny_tekst}")
    except Exception as e:
        print(f"DEBUG ERROR: {traceback.format_exc()}")
        await interaction.followup.send("nawet mój pijacki mózg *uuuuurp* nie ma siły teraz na błędy w kodzie... 🙄")

# Komenda /reset
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