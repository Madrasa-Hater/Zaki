## Zaki
Zaki is an AI Discord bot that I made. It talks like a human and acts like a human. I'm looking forward to make it even more human. It even has memory!!!!!!!!!!!!!!!!!!!!!!!!!!!

## Features
- Long-term memory
- Image recognition
- Human way of speaking
- remembers things that werent directed at him

## How to use the bot?
Just mention/ping it on Discord and it will talk to you!!11!!

- The file should look something like this for you
```py
# IMPORTANT:
# Only edit the empty spaces where values go.
# Leave everything else exactly as it is.

# Paste your Discord bot token between the quotation marks.
BOT_TOKEN = ""

# Paste your Groq API key between the quotation marks.
GROQ_API_KEY = ""

# Paste your weather API key between the quotation marks.
WEATHER_API_KEY = ""

# Add the Discord user IDs that are allowed to use the bot's admin features
#
# Example with one ID:
# [123456789]
#
# Example with several IDs:
# [123456789, 987654321, 555555555]
#
# Leave it as [] if you do not want to add any IDs yet.
APPROVED_IDS = []

# your system instructions go here, they can be multiline (put them between the 3 quotes)
system_instructions = """"""
# your model goes here. Preferrbly stay with the default module.
MODEL = "openai/gpt-oss-20b"
```
## How to set up the bot?
- Rename _settings.py.example to _settings.py
- Go to the `_settings.py` file, everything you need will be there, like the system instructions, memory fetch limit, model, vision model, etc...
