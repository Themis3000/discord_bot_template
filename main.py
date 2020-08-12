import os
import discord
from discord.ext import commands
from utils.config import MainConfig

config = MainConfig()

client = commands.Bot(command_prefix="!",
                      status=discord.Status.idle)

client.client = client


@client.event
async def on_ready():
    print("Startup complete")
    await client.change_presence(status=discord.Status.online)


for file in os.listdir("cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        client.load_extension(f"cogs.{name}")


if __name__ == "__main__":
    TOKEN = os.environ.get("TOKEN")
    assert TOKEN is not None, "Environment variable \"TOKEN\" does not exist, please assign this to your bot's token value"
    client.run(TOKEN)
