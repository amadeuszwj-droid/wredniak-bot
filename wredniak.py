import os
import discord
from discord import app_commands
from discord.ext import commands
from google import genai
from flask import Flask, request
from threading import Thread
import requests

# 1. KONFIGURACJA
DISCORD_TOKEN = os.environ.get("WREDNIAK_DISCORD_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
ai_client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-3.1-flash-lite"

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

# 3. API DLA KICKA
app = Flask('')
@app.route('/wredny')
def wredny_api():
    kogo = request.args.get('kogo', 'widzowie')
    response = ai_client.models.generate_content(
        model=MODEL_NAME,
        contents=[f"Zniszcz tego celu: {kogo}"],
        config={"system_instruction": WREDNIAK_PERSONALITY}
    )
    return response.text

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 4. BOT DISCORD
bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

@bot.tree.command(name="wredniak", description="Wredniak atakuje!")
async def wredniak(interaction: discord.Interaction, kogo: str):
    await interaction.response.defer()
    response = ai_client.models.generate_content(
        model=MODEL_NAME,
        contents=[f"Zniszcz tego celu: {kogo}"],
        config={"system_instruction": WREDNIAK_PERSONALITY}
    )
    await interaction.followup.send(response.text)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.run(DISCORD_TOKEN)