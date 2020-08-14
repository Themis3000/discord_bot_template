"""
Uses class Config to define all type conversion functions for main config.yaml file
"""
from utils.config import Config
import discord

config = Config("./config.yaml")

status_converter_dict = {"online": discord.Status.online,
                         "offline": discord.Status.offline,
                         "idle": discord.Status.idle,
                         "dnd": discord.Status.dnd,
                         "invisible": discord.Status.invisible}

activity_converter_dict = {"game": discord.Game,
                           "streaming": discord.Streaming,
                           "custom": discord.CustomActivity}


@config.register_get_handler("discord_presence.ready.status")
@config.register_get_handler("discord_presence.startup.status")
def status_converter(value):
    if value in status_converter_dict:
        return status_converter_dict[value]
    return status_converter_dict["online"]


@config.register_get_handler("discord_presence.ready.activity")
@config.register_get_handler("discord_presence.startup.activity")
def presence_converter(value):
    if value["type"] in activity_converter_dict:
        return activity_converter_dict[value["type"]](name=value["text"])
    return None
