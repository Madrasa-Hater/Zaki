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

# i should probably switch to the logging library
@_client.event
async def on_ready():
    print("=" * 50)
    print("Starting Zaki startup checks...")
    print("=" * 50)

    # bot info
    print(f"Logged in as {_client.user}")
    print(f"Bot ID: {_client.user.id}")
    print(f"Guilds: {len(_client.guilds)}")
    print(f"Latency: {_client.latency * 1000:.0f}ms")

    # Database check
    try:
        init_memory_db()
        show_all_memory()
        print("[PASS] Memory database")
    except Exception as e:
        print(f"[FAIL] Memory database: {e}")

    # AI backend check
    # should i even call it a backend lol
    try:
        test_response = generate_text("Reply with exactly: OK")
        print(f"[PASS] AI backend ({test_response[:50]})")
    except Exception as e:
        print(f"[FAIL] AI backend: {e}")

    # Memory size check
    try:
        memory = show_all_memory()
        memory_size = len(memory)

        print(f"Memory size: {memory_size:,} characters")

        if memory_size > 50000:
            print("[WARN] Memory is getting large")
    except Exception as e:
        print(f"[FAIL] Memory size check: {e}")

    # Sync slash commands
    try:
        synced = await _client.tree.sync()
        print(f"[PASS] Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"[FAIL] Command sync: {e}")

    # Guild permissions check
    print("\nGuild checks:")
    for guild in _client.guilds:
        me = guild.me

        if me is None:
            continue

        missing = []

        if not me.guild_permissions.send_messages:
            missing.append("Send Messages")

        if not me.guild_permissions.read_messages:
            missing.append("Read Messages")

        if not me.guild_permissions.embed_links:
            missing.append("Embed Links")

        if missing:
            print(f"[WARN] {guild.name}: Missing {', '.join(missing)}")
        else:
            print(f"[PASS] {guild.name}")

    print("=" * 50)
    print("Zaki is ready.")
    print("=" * 50)
    
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
    if ctx.author.id in APPROVED_IDS:
        deleteAllRows()
        await ctx.reply("deleted all of the memory")
    else:
        await ctx.send("You are not admin vro")

@_client.hybrid_command(name="memory", description="shows the memory")
async def memory(ctx: commands.Context):
    """shows the memory in discord. sends them chunked if the message is too long and says 'nothin to show' if the bot has no thought xD"""
    if ctx.author.id in APPROVED_IDS:
        memory = show_all_memory()
        if not memory:
            await ctx.reply("this bot has no thought...", ephemeral=True)
            return

        # splits the message into chunks (was ported from an old bot)
        chunks = [memory[i:i + 2000] for i in range(0, len(memory), 2000)]

        await ctx.reply(chunks[0])
        for chunk in chunks[1:]:
            await ctx.send(chunk, ephemeral=True)
    else:
        await ctx.send("You are not an admin bro")

@_client.hybrid_command(name="_help", description='outputs a list of avaliable commands')
async def _help(ctx:commands.Context):
    embed = discord.Embed(
        title='PWD of commands', description="""
**1.** /reset_memory
- resets the memory of the bot by deleting every row
**2.* /memory
- shows the memory of the bot
"""
    )
    await ctx.send(embed=embed)
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