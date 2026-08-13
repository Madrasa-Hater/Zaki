# VIVE LA PROGRAMMATION!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# - __Devion__
# this file was directly ported from my old project. Although I'm going to modernize it a bit
from groq import Groq
from _settings import *
import base64
import sqlite3
import discord
import datetime

client = Groq(api_key=GROQ_API_KEY)
con = sqlite3.connect("db.memory")
cur = con.cursor()


def init_memory_db():
    def log(text:str):
        print(f"[init_memory_db] {text}")
    try:
        log("Initializing the database...")
        cur.execute("CREATE TABLE IF NOT EXISTS memory(name, date, message, channel, server, your_response, was_directed_at_you)")
        con.commit()
        log("Initilization done!")
    except Exception as e:
        log(f"Unhandled exception: {e}")

def show_all_memory():
    rows = cur.execute("""
        SELECT name, date, message, your_response
        FROM memory
        ORDER BY date
    """).fetchall()

    return "\n".join(
        f"[{date}] {name}: {message}\nAssistant: {response}"
        for name, date, message, response in rows
    )

def write_memory(message: discord.Message, bot_response: str, client: discord.Client):
    cur.execute(
        """
        INSERT INTO memory
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            message.author.name,
            datetime.datetime.now().isoformat(),
            message.content,
            getattr(message.channel, "name", None),
            message.guild.name if message.guild else None,
            bot_response,
            client.user is not None and client.user in message.mentions
        )
    )
    con.commit()
def generate_text(text:str, model:str = MODEL):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_instructions
                },
                {
                    "role": "user",
                    "content": text,
                }
            ],
            model=model
        )

        return chat_completion.choices[0].message.content
    except Exception as e:
        if 'does not exist or you do not have access to it' in str(e):
            return f'uh oh the `{MODEL}` model is invalid'
        else:
            return f"Unhandled error in generate_text: {e}"

def generate_text_img(text:str, image_path:str):
    try:
        def encode_image(image_path_):
            with open(image_path_, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')

        base64_image = encode_image(image_path)

        # Fix: properly detect MIME type instead of hardcoding jpeg
        ext = image_path.split('.')[-1].lower()
        mime = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "webp": "image/webp"
        }.get(ext, "image/jpeg")

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_instructions
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": text},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime};base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
        )

        return chat_completion.choices[0].message.content
    except Exception as e:
        if 'does not exist or you do not have access to it' in str(e):
            return f'uh oh the `{MODEL}` model is invalid'
        else:
            return f"Unhandled error in generate_text: {e}"


def read_file(filename):
    with open(filename, "r", encoding="utf-8") as content:
        return content.read()
    
def write_to_file(filename:str, text:str) -> None:
    with open(filename, 'a', encoding='utf-8') as content:
        content.write(text)

if __name__ == "__main__":
    init_memory_db()
    msg = input("You: ")
    if 'showMemory' in msg:
        show_all_memory()
    response = generate_text(text=msg)
    print(response)