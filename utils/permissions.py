"""
Various functions that act as shortcuts to check permissions given a context
"""
import discord


def can_send(ctx):
    """
    Checks if bot can send messages in the context's channel
    :param ctx: Context
    :return: Boolean
    """
    return isinstance(ctx.channel, discord.DMChannel) or ctx.channel.permissions_for(ctx.guild.me).send_messages


def can_embed(ctx):
    """
    Checks if bot can embed content in the context's channel
    :param ctx: Context
    :return: Boolean
    """
    return isinstance(ctx.channel, discord.DMChannel) or ctx.channel.permissions_for(ctx.guild.me).embed_links


def can_upload(ctx):
    """
    Checks if bot can upload content in the context's channel
    :param ctx: Context
    :return: Boolean
    """
    return isinstance(ctx.channel, discord.DMChannel) or ctx.channel.permissions_for(ctx.guild.me).attach_files


def can_react(ctx):
    """
    Checks if bot can react in the context's channel
    :param ctx: Context
    :return: Boolean
    """
    return isinstance(ctx.channel, discord.DMChannel) or ctx.channel.permissions_for(ctx.guild.me).add_reactions


def is_nsfw(ctx):
    """
    Checks if the context's channel is tagged 'not safe for work'
    :param ctx: Context
    :return: Boolean
    """
    return isinstance(ctx.channel, discord.DMChannel) or ctx.channel.is_nsfw()
