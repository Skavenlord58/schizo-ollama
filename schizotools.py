import re
import disnake
from disnake.ext import commands
import requests
from bottoken import TOKEN
import json

# split the URL for later use
API_URL = "http://localhost:11434"
OLLAMA_URL = f"{API_URL}/api/chat"

# use the exact model name you are using for `ollama run model:version` command
MODEL = "schizo:8k"

SYSTEM_PROMPT = """
Jsi analyzační nástroj, který má zpracovávat zprávy uživatelů na Discordu.
Dostaneš seznam posledních zpráv z daného kanálu. Každá zpráva má autora a obsah.
Pokud zpráva odpovídá na jinou zprávu, používá formát:
`Autor (-> Odpovídá): obsah zprávy`
Jinak použij formát:
`Autor: obsah zprávy`

Tvým úkolem je:
1) stručně shrnout celou konverzaci ("Shrnutí konverzace:"),
2) pak pro každého uživatele, který ve zprávách vystupuje, napsat samostatný odstavec ve formátu `Jméno: ...`.

Nevymýšlej si informace, vycházej jen z toho, co je v daných zprávách.
Pokud pro některého uživatele není dost informací, napiš to jasně.
Výstup by měl mít nejlépe:
- jeden souhrnný řádek nebo odstavec pro konverzaci,
- poté jeden nebo více uživatelských bloků `Jméno: ...`.
"""

DB_NAME = "usersdb.json"

CHANNEL_ID = "1000800481397973052"  # General: 1000800481397973052; ITPero: 786625189038915625

NUM_OF_MESSAGES = 200
TIMEOUT = 300

intents = disnake.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

def append_data_to_user(key, text):
    try:
        with open(DB_NAME, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    data[key] = data.get(key, "") + text

    with open(DB_NAME, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

async def analyze_users():
    messages_payload = await fetch_last_messages(NUM_OF_MESSAGES)
    if not messages_payload:
        print("No messages found to analyze.")
        return {}

    model_response = await query_model("channel_analysis", messages_payload)
    if not model_response:
        print("No response from model.")
        return {}

    parsed = parse_analysis_output(model_response)
    if not parsed:
        append_data_to_user("conversation", model_response + "\n")
        return {"conversation": model_response}

    for user_key, text in parsed.items():
        append_data_to_user(user_key, text + "\n")

    return parsed


def parse_analysis_output(output):
    entries = {}
    current_key = None
    current_lines = []

    def flush_current():
        nonlocal current_key, current_lines
        if current_key is None:
            return
        entries[current_key] = "\n".join(current_lines).strip()
        current_key = None
        current_lines = []

    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if re.match(r'^(celá konverzace|celkově|shrnutí)\s*[:\-–]', line, re.IGNORECASE):
            flush_current()
            summary = line.split(":", 1)[1].strip() if ":" in line else line
            entries["conversation"] = summary
            continue

        user_match = re.match(r'^([\wěščřžýáíéóúůĚŠČŘŽÝÁÍÉÓÚŮ\- ]+)\s*[:\-–]\s*(.*)$', line)
        if user_match:
            flush_current()
            current_key = user_match.group(1).strip()
            current_lines = [user_match.group(2).strip()]
            continue

        if current_key is not None:
            current_lines.append(line)
        else:
            entries.setdefault("conversation", "")
            entries["conversation"] = (entries["conversation"] + "\n" + line).strip()

    flush_current()
    return entries


async def fetch_last_messages(limit):
    channel = bot.get_channel(int(CHANNEL_ID))
    if channel is None:
        channel = await bot.fetch_channel(int(CHANNEL_ID))

    if channel is None:
        raise RuntimeError(f"Channel {CHANNEL_ID} not found")

    history = []
    async for message in channel.history(limit=limit, oldest_first=False):
        if message.author.bot:
            continue

        content = message.clean_content.strip()
        if not content:
            continue

        author = message.author.name
        reply_to = None
        if message.reference and message.reference.message_id:
            resolved = message.reference.resolved
            if isinstance(resolved, disnake.Message):
                reply_to = resolved.author.name
            else:
                try:
                    referenced = await channel.fetch_message(message.reference.message_id)
                    reply_to = referenced.author.name
                except Exception:
                    reply_to = None

        if reply_to:
            history.append(f"{author} (-> {reply_to}): {content}")
        else:
            history.append(f"{author}: {content}")

    return "\n".join(history)


async def query_model(user, pyld_data):
    payload = {
        "model": MODEL,
        "stream": False,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": pyld_data},
        ],
    }
    print(f"Analysing messages from {user}...")

    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT)
        r.raise_for_status()
    except requests.exceptions.RequestException as exc:
        print(f"Ollama request failed: {exc}")
        return None

    reply = r.json().get("message", {}).get("content")
    if not isinstance(reply, str):
        print("Unexpected response from Ollama:", r.text)
        return None

    print("Got a reply! Adding it to the DB!")
    return reply


@bot.event
async def on_ready():
    print(f'Schizotools is ready. Ollama returned {requests.get(url=API_URL).status_code}')
    print("Running in autonomous mode!")

    try:
        await analyze_users()
    except Exception as exc:
        print(f"Error during analysis: {exc}")
    finally:
        if not bot.is_closed():
            await bot.close()

bot.run(TOKEN)