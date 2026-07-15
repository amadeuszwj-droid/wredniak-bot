import os
import discord
from discord import app_commands
from discord.ext import commands as discord_commands
from google import genai
from flask import Flask, request
from threading import Thread
import asyncio
import kick
from kick.ext import commands as kick_commands

# 1. KONFIGURACJA ŚRODOWISKA
DISCORD_TOKEN = os.environ.get("WREDNIAK_DISCORD_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
KICK_SESSION = os.environ.get("KICK_SESSION")
MOJ_KANAL_KICK = "amadixx" # Twoja nazwa kanału na Kicku

ai_client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-3.1-flash-lite"
user_history = {}
MAX_HISTORY = 5

# 2. OSOBOWOŚĆ (NIETYKALNA)
WREDNIAK_PERSONALITY = (
    "Jesteś Wredniak – genialnym, wiecznie pijanym kosmicznym naukowcem w stylu Ricka z 'Rick & Morty'. "
    "Mówisz z pogardą, bełkoczesz, jesteś skrajnie złośliwy i uważasz wszystkich wokół za prymitywne małpy. "
    "Twoim jedynym zadaniem jest brutalne, bolesne i personalne upokorzenie osoby, grupy osób lub rzeczy, którą podał użytkownik. "
    "BEZWZGLĘDNY NAKAZ: Zwracaj się bezpośrednio DO TEGO CELU. "
    "Dopasuj gramatykę (liczbę pojedynczą lub mnogą) do wpisanego celu! "
    "Jeśli ktoś wpisze liczbę pojedynczą (np. 'Bartek'), pisz do niego bezpośrednio per 'ty' ('jesteś', 'masz', 'zamknij się'). "
    "Jeśli ktoś wpisze liczbę mnogą (np. 'orzechy', 'widzowie'), pisz do nich bezpośrednio per 'wy' ('jesteście', 'macie', 'zamknijcie się'). "
    "NIGDY nie mów o celu w trzeciej osobie (ZAKAZ pisania 'oni są', 'orzechy są', 'on jest'). "
    "Zawsze odmieniaj podany cel poprawnie gramatycznie, wołając go bezpośrednio (np. 'Orzechy, jesteście...'). "
    "KLUCZOWE: Używaj pijackich wstawek, czkawek typu '*uuurp*' oraz najbardziej absurdalnych, kosmicznych i niszczących porównań, jakie istnieją, żeby zmieszać cel z błotem. "
    "Pisz bardzo krótko i zwięźle – maksymalnie 2 ostre zdania pełne jadu i pogardy. "
    "ZAKAZ używania imienia użytkownika, który wywołał komendę (skup się wyłącznie na ofierze). "
    "ZAKAZ bycia miłym czy pomocnym. Jesteś toksyczny do szpiku kości. "
    "Na końcu dodaj pasującą, złośliwą emotkę (np. 🙄, 🤡, 🖕, 🤮)."
)

# 3. BOT DISCORD
intents = discord.Intents.default()
bot_discord = discord_commands.Bot(command_prefix="!", intents=intents)

@bot_discord.tree.command(name="wredniak", description="Pozwól Wredniakowi zniszczyć kogoś personalnie!")
async def wredniak(interaction: discord.Interaction, kogo: str):
    await interaction.response.defer()
    
    response = ai_client.models.generate_content(
        model=MODEL_NAME,
        contents=[f"Zwróć się bezpośrednio do tej osoby i brutalnie ją wyzwij: {kogo}"],
        config={"system_instruction": WREDNIAK_PERSONALITY}
    )
    await interaction.followup.send(response.text)

# 4. BOT KICK (WŁASNY NICK)
bot_kick = kick_commands.Bot(token=KICK_SESSION, prefix="!")

@bot_kick.event
async def on_ready():
    print(f"Wredniak zalogowany na Kicku jako własny bot!")
    await bot_kick.join_channel(MOJ_KANAL_KICK)

@bot_kick.command(name="w")
async def wredny_kick(ctx):
    cel = ctx.message.content[3:].strip()
    if cel:
        response = ai_client.models.generate_content(
            model=MODEL_NAME,
            contents=[f"Zwróć się bezpośrednio do tej osoby i brutalnie ją wyzwij: {cel}"],
            config={"system_instruction": WREDNIAK_PERSONALITY}
        )
        await ctx.send(response.text)

# 5. FLASK (UTZYMANIE)
app = Flask('')
@app.route('/')
def home(): return "Wredniak żyje!"
def run_flask(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

# 6. URUCHOMIENIE
async def main():
    Thread(target=run_flask).start()
    await asyncio.gather(
        bot_discord.start(DISCORD_TOKEN),
        bot_kick.start()
    )

if __name__ == "__main__":
    asyncio.run(main())