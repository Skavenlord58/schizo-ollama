# schizo-ollama

## Description
Short python script for running a discord bot, that is using locally hosted ollama model for responses.

This was created as a simple PoC for me to learn on how do models, system prompts and ollama API work.

The bot is called "Schizo" mostly because of his chaotic nature.

## How to run

### Create a Discord BOT token
- Visit the [Discord Developer Portal](https://discord.com/developers/applications) and create a new application
- Follow the instructions on the [Discord Bots Quick-start Guide](https://docs.discord.com/developers/quick-start/getting-started), if you are not sure on what to do

- Create a file called `bottoken.py` and supple the token there (omitted from repo for obvious reasons):
```py
TOKEN="MTA_ThisIsMyBOTToken69_etc"
```

### Set up Ollama server
- This bot is using a custom model setting:

```
# Modelfile
FROM jobautomation/OpenEuroLLM-Czech:latest
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER num_ctx 8192
SYSTEM "Vždy budeš odpovídat správnou a přirozenou češtinou. Jsi užitečný a přátelský asistent, který pomáhá uživatelům s jejich dotazy v češtině. Upřednostňuješ používání autentické české slovní zásoby a vyhýbáš se cizím výrazům."
```
- The system prompt in the Modelfile is the default one, it is changed by the API request anyways.

- Basic setup:
```sh
ollama create schizo:8k -f Modelfile
ollama run schizo:8k
# When the chat comes up type "Ahoj!" and press ENTER.
# After the model starts responsing press CTRL-D.
ollama ps # check if model is still running

# after work is done
ollama stop schizo:8k
```

### Running this script
- Requirements:
 - python3
    - disnake
    - requests

- Running the script:
```py
python3 ./main.py
```

## Interacting with the bot
- The bot will respond if you tag him directly, or reply to his message.
- The script can be modified to have more function, but this is on somebody else.