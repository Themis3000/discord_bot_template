"""
Various decorator functions for commands.command decorated functions that perform checks to judges weather or not the
function should be ran
"""
from discord.ext import commands


def example():
    def predicate(ctx):
        return True
    return commands.check(predicate)
