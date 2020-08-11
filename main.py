import os
import discord
from discord.ext import commands

client = commands.Bot(command_prefix="!",
                      status=discord.Status.idle)


# Announce successful startup
@client.event
async def on_ready():
    print("Startup complete")
    await client.change_presence(status=discord.Status.online)

# Load all "cogs"
for file in os.listdir("cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        client.load_extension(f"cogs.{name}")

# Check if token var is set and run bot
TOKEN = os.environ.get("TOKEN")
assert TOKEN is not None, "Environment variable \"TOKEN\" does not exist, please assign this to your bot's token value"
client.run(TOKEN)
