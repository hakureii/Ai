#!/usr/bin/env python3

import os, discord, asyncio
from discord.ext import commands

prefix = "ai "

bot = commands.Bot(prefix)

@bot.event
async def on_reaction_add(reaction: discord.Reaction, user):
    if reaction.emoji == "💩":
        await reaction.remove(user)

@bot.event
async def on_ready():
    await asyncio.sleep(5 * 60 * 60)
    os.remove(os.getenv("CONDITION"))
    await bot.close()

bot.run(os.getenv("AI"))
