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
    init_memory_db()
    print("ich suis ready")

    await _client.tree.sync()


@_client.event
async def on_message(message: discord.Message):
    try:
        print(f"{message.author.name}: {message.content}")
        context = f"Message: {message.content}, Context: Name: {message.author.name}, channel name: {message.channel.name}, server name: {message.guild.name}, current time: {datetime.datetime.now()} Your memory: {show_all_memory()}"
        if message.author == _client.user:
            return
        if _client.user in message.mentions:
            async with message.channel.typing():
                if message.attachments and len(message.attachments) == 1:
                    response = generate_text_img(context, message.attachments[0].url)
                    await send_chunked(message, response)
                    print("Writing memory...")
                    write_memory(message=message, bot_response=response, client=_client)
                    print("Done recording memory!")
                else:
                    print("Bot in message mentions, responding...")
                    response = generate_text(context)

                    await send_chunked(message, response)

                    print("Writing memory...")
                    write_memory(message=message, bot_response=response, client=_client)
                    print("Done recording memory!")
        elif message.content.startswith("!memory"):
            try:
                await send_chunked(message, show_all_memory())
            except Exception as e:
                if 'Cannot send an empty message' in str(e):
                    await message.reply("The memory is empty.")
    except Exception as e:
        await message.reply(f"Unhandled Error: {str(e)}")

@_client.hybrid_command(name="reset_memory", description="resets the memory")
async def reset_memory(ctx:commands.Context):
    deleteAllRows()
    await ctx.reply("deleted all of the memory")

@_client.hybrid_command(name="show_memory", description="shows the memory")
async def reset_memory(ctx: commands.Context):
    memory = show_all_memory()

    if not memory:
        await ctx.reply("nothin to show")
        return

    chunks = [memory[i:i + 2000] for i in range(0, len(memory), 2000)]

    await ctx.reply(chunks[0])
    for chunk in chunks[1:]:
        await ctx.send(chunk)

try:
    _client.run(BOT_TOKEN)
except Exception as e:
    if "Cannot connect to host" in str(e):
        print("You probably don't have internet enabled or a VPN is blocking this vro")
    elif "Improper token" in str(e):
        print("please check whether your token is valid")
    else:
        print(f"Unhandled error: {e}")