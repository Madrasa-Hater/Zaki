"""
This is a Discord bot made using Discord.py version '2.7.1'. The planned features are down below.

-- Planned features --
1. AI Chatbot [ADDED]
2. SQLite3 Memory for the AI chatbot [ADDED]
3. Agentic AI
4. A complete dashboard command (/dashboard)

--- Planned commands --
1. /dashboard
2. /memory
3. /restart
"""

import discord
import openai
from discord.ext import commands

from helpers import *
from _settings import *
import datetime
_client = commands.AutoShardedBot(command_prefix="bro", intents=discord.Intents.all())

@_client.event
async def on_ready():
    # initializes the memory (checks if it is already initalized)
    init_memory_db()
    print("the bot is ready to be used")

    # syncs the bot slash commands
    await _client.tree.sync()

@_client.event
async def on_message(message: discord.Message):
    try:
        print(f"{message.author.name}: {message.content}")
        # builds the context necessary for the bot to respond correctly
        context = f"Message: {message.content}, Context: Name: {message.author.name}, channel name: {message.channel.name}, server name: {message.guild.name}, current time: {datetime.datetime.now()} Your memory: {show_all_memory()}"
        async with message.channel.typing():
            response = generate_text(context)

            # do NOT uncomment the following line unless you know whatt you are doing
            # what does this line do?
            # it prints the whole context to debug certain errors
            await message.reply(context if len(context) <= 2000 else "contextt too long.")
            await message.reply(response)

            print("Writing memory...")
            write_memory(message=message, bot_response=response, client=_client)
            print("Done recording memory!")
    elif message.content.startswith("!memory"):
        try:
            await message.reply(show_all_memory())
        except Exception as e:
            if 'Cannot send an empty message' in str(e):
                await message.reply("The memory is empty.")

_client.run(BOT_TOKEN)
