from discord.ext import commands
import os

TOKEN = os.environ.get('ESTATE_BOT_TOKEN')
client = commands.Bot(command_prefix='^', case_insensitive=True)

extensions = ['oikotie']


@client.event
async def on_ready():
    print("Loading complete")

if __name__ == "__main__":
    for extension in extensions:
        try:
            client.load_extension(extension)
            print(f"{extension} loaded successfully")
        except Exception as error:
            print(f"{extension} loading failed [{error}]")

    client.run(TOKEN)
