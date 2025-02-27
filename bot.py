import discord
from discord.ext import commands
import aiohttp
import logging

logging.basicConfig(level=logging.INFO)

TOKEN = 'BOT_TOKEN'  # Remplace par ton token de bot
API_URL = 'https://blagues.api.silverdium.fr/api'


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

valid_types = {
    "Aléatoire": "all",
    "Tout public": "global",
    "Humour noir": "dark",
    "Blague de dev": "dev",
    # "Blague 18+": "limit",
    # "Humour beauf": "beauf",
    # "Blagues de blondes": "blondes"
}


async def get_joke(type=None, id=None):
    """ Récupère une blague depuis l'API """
    joke_url = f"{API_URL}/?random=true" if type == 'all' else f"{API_URL}/?type={type}&random=true"
    
    if id:
        joke_url = f"{API_URL}/?id={id}"

    async with aiohttp.ClientSession() as session:
        async with session.get(joke_url) as response:
            if response.status == 200:
                return await response.json()
    return None


class JokeView(discord.ui.View):
    """ Vue pour le bouton 'Une autre' """

    def __init__(self, type):
        super().__init__()
        self.type = type

    @discord.ui.button(label="🔄 Une autre", style=discord.ButtonStyle.primary)
    async def another_joke(self, interaction: discord.Interaction, button: discord.ui.Button):
        """ Gère le clic sur le bouton """
        joke_data = await get_joke(type=self.type)

        if not joke_data:
            await interaction.response.send_message("❌ Impossible de récupérer une nouvelle blague.", ephemeral=True)
            return

        joke = joke_data.get('joke', '❌ Blague introuvable.')
        answer = joke_data.get('answer', '❌ Réponse introuvable.')
        joke_id = joke_data.get('id', 'Inconnu')
        joke_type = joke_data.get('type', 'Inconnu')

        embed = discord.Embed(
            title="🤣   Blague",
            description=f"## {joke}",
            color=discord.Color(int("9316d3", 16))
        )

        embed.add_field(name="Réponse", value=f"**||{answer}||**", inline=False)
        embed.set_footer(text=f"ID : {joke_id} • Type : {joke_type}  |  [fournie par Blagues API](https://www.blagues-api.fr/)")
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/745789765522178088.png")

        # Utiliser send_message pour envoyer un nouveau message à chaque clic
        await interaction.response.send_message(embed=embed, view=JokeView(self.type))



class JokeTypeSelect(discord.ui.Select):
    """ Menu déroulant pour choisir le type de blague """

    def __init__(self):
        options = [
            discord.SelectOption(label=name, value=value) for name, value in valid_types.items()
        ]
        super().__init__(placeholder="Choisissez un type de blague...", options=options)

    async def callback(self, interaction: discord.Interaction):
        type_selected = self.values[0]
        joke_data = await get_joke(type=type_selected)

        if not joke_data:
            await interaction.response.send_message("❌ Impossible de récupérer une blague.", ephemeral=True)
            return

        joke = joke_data.get('joke', '❌ Blague introuvable.')
        answer = joke_data.get('answer', '❌ Réponse introuvable.')
        joke_id = joke_data.get('id', 'Inconnu')
        joke_type = joke_data.get('type', 'Inconnu')

        embed = discord.Embed(
            title="🤣   Blague du jour",
            description=f"## {joke}",
            color=discord.Color(int("9316d3", 16))
        )

        embed.add_field(name="Réponse", value=f"**||{answer}||**", inline=False)
        embed.set_footer(text=f"ID : {joke_id} • Type : {joke_type}  |  fournie par Blagues API (https://www.blagues-api.fr/)")
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/745789765522178088.png")

        await interaction.response.send_message(embed=embed, view=JokeView(type_selected))


class JokeTypeView(discord.ui.View):
    """ Vue avec le menu déroulant pour choisir un type de blague """

    def __init__(self):
        super().__init__()
        self.add_item(JokeTypeSelect())

@bot.event
async def on_ready():
    print(f'{bot.user} est connecté et prêt !')

    try:
        guild = discord.Object(id='SERV_ID')  # ID du serveur Discord
        await bot.tree.sync(guild=guild)
        print("Commandes slash synchronisées !")
    except Exception as e:
        print(f"Erreur lors de la synchronisation des commandes : {e}")

    await bot.change_presence(
        activity=discord.Game(name="blagues API de draftMan")
    )

@bot.tree.command(name="blague", description="Récupère une blague avec sélection interactive")
async def blague(interaction: discord.Interaction):
    await interaction.response.send_message("🎭 Choisissez un type de blague :", view=JokeTypeView(), ephemeral=True)


bot.run(TOKEN)