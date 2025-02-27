import discord
from discord.ext import commands
import aiohttp
import logging

logging.basicConfig(level=logging.INFO)

TOKEN = 'bot token'  # Remplace par ton token de bot
API_URL = 'https://blagues.api.silverdium.fr/api'

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

valid_types = ['general', 'dev']

@bot.event
async def on_ready():
    print(f'{bot.user} est connecté et prêt !')

    try:
        guild = discord.Object()
        await bot.tree.sync(guild=guild)
        print("Commandes slash synchronisées !")
    except Exception as e:
        print(f"Erreur lors de la synchronisation des commandes : {e}")

    await bot.change_presence(
        activity=discord.Game(name="blagues API de draftMan")
    )



@bot.tree.command(name="blague", description="Récupère une blague")
async def blague(interaction: discord.Interaction, type: str = "general"):
    if type not in valid_types:
        await interaction.response.send_message("Désolé, ce type de blague n'est pas valide. Utilisez 'general' ou 'dev'.")
        return

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{API_URL}/?type={type}&random=true') as response:
                if response.status == 200:
                    data = await response.json()
                    joke = data.get('joke', 'Désolé, je n\'ai pas pu récupérer de blague.')
                    answer = data.get('answer', 'Désolé, je n\'ai pas pu récupérer de blague.')
                    await interaction.response.send_message(f"Blague :\n## {joke}\n||{answer}||\n-# https://blagues.api.silverdium.fr/")
                else:
                    await interaction.response.send_message("Désolé, je n'ai pas pu récupérer de blague cette fois.")
    except Exception as e:
        print(f"Erreur lors de la récupération de la blague : {e}")
        await interaction.response.send_message("Une erreur est survenue, veuillez réessayer plus tard.")

bot.run(TOKEN)
