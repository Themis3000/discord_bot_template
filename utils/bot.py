"""
various useful message based bot utils
"""
from utils.emoji import from_numbers, to_number
import discord
from discord.ext import commands
import asyncio
import math


class BotUtils(commands.Cog):
    @staticmethod
    async def numbered_reaction_menu(bot, message: discord.Message, amount: int, allowed_responder: discord.abc.User, timeout=120):
        """Makes a basic numbered reaction menu"""
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

    @staticmethod
    async def pagination_reaction_menu(ctx, bot, item_list: list, page_length: int, prefix: str = None, timeout: str = 60):
        """Makes a paginated message controlled by reactions"""
        page = 1
        max_page = math.ceil(len(item_list) / page_length)
        allowed_responder = ctx.author

        def render_page():
            last_item = page * page_length
            page_list = "\n".join(item_list[last_item - page_length:last_item])
            if prefix is not None:
                return f"{prefix}\n{page_list}"
            return page_list

        message = await ctx.send(render_page())

        if len(item_list) <= page_length:
            return

        await message.add_reaction("◀")
        await message.add_reaction("▶")

        async def update_message():
            await message.edit(content=render_page())

        def check(reaction, sender):
            return sender == allowed_responder and str(reaction.emoji) in ["▶", "◀"]

        while True:
            try:
                reaction, sender = await bot.wait_for('reaction_add', timeout=timeout, check=check)
            except asyncio.TimeoutError:
                return
            else:
                if str(reaction.emoji) == "▶":
                    if page < max_page:
                        page += 1
                        await update_message()
                elif page > 1:
                    page -= 1
                    await update_message()
                await reaction.remove(sender)
