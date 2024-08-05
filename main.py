import os
import io
import json
import asyncio
import discord
import requests
from PIL import Image
from discord.ext import commands
import google.generativeai as genai

prefix = ["> "]
intents = discord.Intents.all()
genai.configure(api_key=os.getenv("GEMINI"))

bot = commands.Bot(prefix, intents=intents)


global ai_chan, chat_model
ai_chan = False
chat_model = False

@bot.command(name="reboot", help="merge the current github source!")
async def reboot(ctx: commands.Context):
    await ctx.send(content="soon™")
    await bot.close()

@bot.slash_command(name="chat_mode", description="enable or disable ai chat mode!")
async def chat_mode(interaction: discord.Interaction, model: discord.Option(str, choices=["gemini-pro", "gemini-flash"])):
    with open("settings.json") as file:
        settings = json.load(file)
    global ai_chan, chat_model
    if ai_chan:
        ai_chan = False
        await interaction.response.send_message(content="Chat mode is already enabled! \n-# you can say \"bye\" to disable it. ")
    else:
        ai_chan = interaction.channel
        await interaction.response.send_message(content="Ai Enabled!")
    if not chat_model:
        system_instruction=None
        if model == "gemini-pro":
            model = "gemini-1.0-pro"
        elif model == "gemini-flash":
            model = "gemini-1.5-flash"
            system_instruction = None
        model_tmp = genai.GenerativeModel(model_name=model,system_instruction=system_instruction,safety_settings=settings[1],generation_config=genai.types.GenerationConfig(candidate_count=1, max_output_tokens=500))
        chat_model = model_tmp.start_chat(history=[genai.protos.Content(settings[0]), genai.protos.Content({'parts': [{'text': 'yes master!'}], 'role': 'model'})])


@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user or message.author.bot:
        return

    if message.content.startswith(prefix[0]):
        await bot.process_commands(message)
        return

    global ai_chan, chat_model
    if ai_chan:
        if message.channel != ai_chan:
            return
        if chat_model:
            await message.channel.trigger_typing()
            author_name = "user: " + message.author.name.lower().replace(".", " ").replace("_", " ") + ", prompt: "
            prompt = list()
            prompt.append(author_name + message.content.lower())
            if message.attachments:
                for attachment in message.attachments:
                    if attachment.content_type.startswith("image/"):
                        image_response = requests.get(attachment.url)
                        image_data = io.BytesIO(image_response.content)
                        image = Image.open(image_data)
                        prompt.append(image)
            try:
                response = chat_model.send_message(prompt).text
            except Exception as e:
                response = "-# " + e.__class__.__name__
            if message.content.lower() == "bye":
                ai_chan = False
                chat_model = False
            await message.reply(content=response)


@bot.event
async def on_ready():
    await asyncio.sleep(5 * 60 * 60)
    os.remove(os.getenv("CONDITION"))
    await bot.close()

bot.run(os.getenv("AI"))
