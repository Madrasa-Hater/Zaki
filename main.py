"""
This is a Discord bot made using Discord.py version '2.7.1'. The planned features are down below.

-- Planned features --
1. AI Chatbot [no memory for now]
2. SQLite3 Memory for the AI chatbot
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

import sqlite3
from helpers import *
from _settings import *

client = commands.AutoShardedBot(command_prefix="bro", intents=discord.Intents.all())

@client.event
async def on_ready():
    print("ich suis ready")

@client.event
async def on_message(message:discord.Message):
    print(f"{message.author.name}: {message.content}")
    if message.author == client.user:
        return
    if client.user in message.mentions:
        print("Bot in message mentions, responding...")

        async with message.channel.typing():
            response = generate_text(message.content)

            await message.reply(response)

            print("done responding")

            print(f"Zaki: {response}")

client.run(BOT_TOKEN)
