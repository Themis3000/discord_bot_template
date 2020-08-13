import os
from discord.ext import commands
from utils.config import Config, converter_dict

config = Config("config.yaml")

# todo make these config calls less verbose
client = commands.Bot(command_prefix=config.settings["essentials"]["command_prefix"],
                      status=converter_dict[config.settings["discord_presence"]["startup"]["status"]],
                      activity=converter_dict[config.settings["discord_presence"]["startup"]["activity"]["type"]](name=config.settings["discord_presence"]["startup"]["activity"]["text"]))


@client.event
async def on_ready():
    print("Startup complete")
    await client.change_presence(status=converter_dict[config.settings["discord_presence"]["ready"]["status"]],
                                 activity=converter_dict[config.settings["discord_presence"]["startup"]["activity"]["type"]](name=config.settings["discord_presence"]["ready"]["activity"]["text"]))


for file in os.listdir("cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        client.load_extension(f"cogs.{name}")


if __name__ == "__main__":
    TOKEN = os.environ.get("TOKEN")
    assert TOKEN is not None, "Environment variable \"TOKEN\" does not exist, please assign this to your bot's token value"
    client.run(TOKEN)
