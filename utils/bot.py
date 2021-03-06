"""
various useful message based bot utils
"""
from utils.emoji import from_numbers, to_number
import discord
from discord.ext import commands


class BotUtils(commands.Cog):
    @staticmethod
    async def numbered_reaction_menu(bot, message: discord.Message, amount: int, allowed_responder: discord.abc.User, timeout=120):
        """
        Makes a basic numbered reaction menu
        """
        reactions = []
        for i in range(amount):
            reaction = from_numbers(i + 1)
            await message.add_reaction(reaction)
            reactions.append(reaction)

        def check(reaction, sender):
            return sender == allowed_responder and str(reaction.emoji) in reactions

        try:
            reaction, sender = await bot.wait_for('reaction_add', timeout=timeout, check=check)
            await message.clear_reactions()
        except:
            return None, None
        else:
            return to_number(reaction.emoji), sender
