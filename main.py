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
        # checks if the message author is not the bot since the bot sometimes mentions itself and replies to itself
        if message.author == _client.user:
            return
        # response logic
        # checks if the bot is mentioned and is not in the blacklist, if all of these conditions are correct the bot responds
        if _client.user in message.mentions and message.author.id not in black_list:
            # shows the 'bot is typing...' thingy idk what is it called
            async with message.channel.typing():
                # made it check only the first attachement cuz all of the groq quota would burn up
                if message.attachments:
                    response = generate_text_img(context, message.attachments[0].url)
                    await send_chunked(message, response)
                    print("Writing memory...")
                    write_memory(message=message, bot_response=response, client=_client)
                    print("Done recording memory!")
                # if no images then respond normally and writeh the memory
                else:
                    print("Bot in message mentions, responding...")
                    response = generate_text(context) # generates the text

                    await send_chunked(message, response)

                    # writes the memory
                    print("Writing memory...")
                    write_memory(message=message, bot_response=response, client=_client) 
                    print("Done recording memory!")
    except Exception as e:
        await message.reply(f"Unhandled Error: {str(e)}")

@_client.hybrid_command(name="reset_memory", description="resets the memory")
async def reset_memory(ctx:commands.Context):
    """Takes no arguments. Deletes all the rows of the memory database which resets the memory"""
    deleteAllRows()
    await ctx.reply("deleted all of the memory")

@_client.hybrid_command(name="show_memory", description="shows the memory")
async def show_memory(ctx: commands.Context):
    """shows the memory in discord. sends them chunked if the message is too long and says 'nothin to show' if the bot has no thought xD"""
    memory = show_all_memory()

    if not memory:
        await ctx.reply("this bot has no thought...")
        return

    # splits the message into chunks (was ported from an old boo)
    chunks = [memory[i:i + 2000] for i in range(0, len(memory), 2000)]

    await ctx.reply(chunks[0])
    for chunk in chunks[1:]:
        await ctx.send(chunk)

# this thing tries to run the bot, if no internet or a vpn/proxy is blocking it it sends an error message. if it is
# an unhandled error it sends 'Unhandled error: <error here>'
try:
    _client.run(BOT_TOKEN)
except Exception as e:
    if "Cannot connect to host" in str(e):
        print("You probably don't have internet enabled or a VPN/proxy is blocking this vro")
    elif "Improper token" in str(e):
        print("please check whether your token is valid")
    else:
        print(f"Unhandled error: {e}")