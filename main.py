import os
from discord.ext import commands
from utils.main_config import config


client = commands.Bot(command_prefix=config["essentials.command_prefix"],
                      status=config["discord_presence.startup.status"],
                      activity=config["discord_presence.startup.activity"])


@client.event
async def on_ready():
    print("Startup complete")
    await client.change_presence(status=config["discord_presence.ready.status"],
                                 activity=config["discord_presence.ready.activity"])


# load cogs
for file in os.listdir("cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        client.load_extension(f"cogs.{name}")


# start bot
if __name__ == "__main__":
    TOKEN = os.environ.get("TOKEN")
    assert TOKEN is not None, "Environment variable \"TOKEN\" does not exist, please assign this to your bot's token value"
    client.run(TOKEN)
