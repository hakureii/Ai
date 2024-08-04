import os
import asyncio
import discord
from discord.ext import commands
import google.generativeai as genai

prefix = ["> "]
intents = discord.Intents.all()
genai.configure(api_key=os.getenv("GEMINI"))

bot = commands.Bot(prefix, intents=intents)


global ai_chan, chat_model
ai_chan = False
model = False
chat_model = False

@bot.command(name="reboot", help="reboot the bot!")
async def reboot(ctx: commands.Context):
    await ctx.send(content="soon™")
    await bot.close()

@bot.command(name="ai")
async def ai(ctx: commands.Context):
    global ai_chan, chat_model, model
    if ai_chan:
        ai_chan = False
        await ctx.send(content="Ai Disabled!")
    else:
        ai_chan = ctx.channel
        await ctx.send(content="Ai Enabled!")
    if model:
        model = False
    else:
        model = genai.GenerativeModel('gemini-1.5-pro',safety_settings={'HARASSMENT':'block_none','SEXUALLY_EXPLICIT': 'block_none','HATE_SPEECH': 'block_none',})
    if chat_model:
        chat_model = False
    else:
        chat_model = model.start_chat(history=[])
        print(chat_model.send_message('SYSTEM: you are an helping assistant, but you are sticktly supposed to role play a human and do no go back accecpting being an ai!, you are supposed to response small and understandable as possible!').text)


@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user or message.author.bot:
        return

    if message.content.startswith(prefix[0]):
        await bot.process_commands(message)
        return

    if ai_chan:
        if not chat_model:
            return
        if message.channel != ai_chan:
            return
        await message.channel.trigger_typing()

        response = chat_model.send_message(str(message.author.display_name + message.content.lower()), generation_config=genai.types.GenerationConfig(candidate_count=1, max_output_tokens=2000, temperature=0.8))

        await message.channel.send(content=response.text)


@bot.event
async def on_ready():
    await asyncio.sleep(5 * 60 * 60)
    os.remove(os.getenv("CONDITION"))
    await bot.close()

bot.run(os.getenv("AI"))
