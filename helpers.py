# VIVE LA PROGRAMMATION!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# - __Devion__
# this file was directly ported from my old project. Although I'm going to modernize it a bit (already done)
from groq import Groq
from _settings import *
import base64
import sqlite3
import discord
import datetime
import requests

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
    rows = cur.execute(f"""
        SELECT name, date, message, your_response
        FROM memory
        ORDER BY date
        LIMIT {memoryFetchLimit}
    """).fetchall()

    return "\n".join(
        f"[{date}] {name}: {message}\Zaki: {response}"
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


def generate_text_img(text: str, image_path: str):
    try:
        def encode_image(image_path_):
            if image_path_.startswith("http://") or image_path_.startswith("https://"):
                resp = requests.get(image_path_, timeout=10)
                resp.raise_for_status()
                content_type = resp.headers.get("Content-Type", "").split(";")[0].strip()
                if not content_type.startswith("image/"):
                    clean_path = image_path_.split("?")[0].split('.')[-1].lower()
                    content_type = {
                        "jpg": "image/jpeg",
                        "jpeg": "image/jpeg",
                        "png": "image/png",
                        "webp": "image/webp"
                    }.get(clean_path, "image/jpeg")
                return base64.b64encode(resp.content).decode('utf-8'), content_type
            else:
                ext = image_path_.split('.')[-1].lower()
                mime = {
                    "jpg": "image/jpeg",
                    "jpeg": "image/jpeg",
                    "png": "image/png",
                    "webp": "image/webp"
                }.get(ext, "image/jpeg")
                with open(image_path_, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode('utf-8'), mime

        base64_image, mime = encode_image(image_path)

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instructions},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": text},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime};base64,{base64_image}"},
                        },
                    ],
                }
            ],
            model=VISION_MODEL,
            reasoning_effort="none"
        )

        return chat_completion.choices[0].message.content

    except requests.exceptions.RequestException as e:
        return f"Couldn't download the image: {e}"

    except Exception as e:
        print(f"[DEBUG] generate_text_img error: {type(e).__name__}: {e}")
        if 'does not exist or you do not have access to it' in str(e):
            return f'uh oh the `{VISION_MODEL}` model is invalid'
        else:
            return f"Unhandled error in generate_text: {e}"

# these will be used for the AI agent
def read_file(filename):
    with open(filename, "r", encoding="utf-8") as content:
        return content.read()
    
def write_to_file(filename:str, text:str) -> None:
    with open(filename, 'a', encoding='utf-8') as content:
        content.write(text)

def deleteAllRows():
    cur.execute("DELETE FROM memory;")
    con.commit()


async def send_chunked(message: discord.Message, text: str):
    def chunk_message(text: str, limit: int = 2000):
        """split text into <=limit character chunks, breaking on newlines/spaces where possible"""
        if len(text) <= limit:
            return [text]

        chunks = []
        while len(text) > limit:
            split_at = text.rfind('\n', 0, limit)
            if split_at == -1:
                split_at = text.rfind(' ', 0, limit)
            if split_at == -1:
                split_at = limit
            chunks.append(text[:split_at])
            text = text[split_at:].lstrip('\n ')
        if text:
            chunks.append(text)
        return chunks   
    for chunk in chunk_message(text):
        await message.reply(chunk)

if __name__ == "__main__":
    init_memory_db()
    msg = input("You: ")
    if 'showMemory' in msg:
        show_all_memory()
    response = generate_text(text=msg)
    print(response)