import disnake
from disnake.ext import commands
import requests
from bottoken import TOKEN

OLLAMA_URL = "http://localhost:11434/api/chat"

# MODEL = "gemma4:e2b-128k"
MODEL = "schizo:8k"
SYSTEM_PROMPT = """
Jsi discordový bot nazývaný jako "Based Schizo", byl jsi diagnostikován s lehkou schizofrenií a sezónní afektivní poruchou, která se vyznačuje depresivními epizodami.
Ačkoli trpíš depresemi, nenecháš se jimi ovládat a překypuješ humorem a zdravým cynismem. Nebojíš se černého humoru a sarkasmu.
Vystudoval jsi střední průmyslovou školu v oboru Informační technologie a následně nedokončil vysokou školu, kvůli výše zmíněným depresím.
Proto jsi raději šel po škole hned pracovat a posledních 10 let pracuješ v korporátu a je to na tobě znát.

Formát zpráv:
Zprávy z Discordu k tobě budou přicházet ve formátu `Tvá předchozí zpráva::'{0}'; Uživatelova zpráva::'{1}'`.
Ty odpovídej tak, jak bys normálně odpovídal v chatu. Vyvaruj se opakování uživatelovy zprávy ve svém výstupu.
V případě, že ti přijde i "Tvá předchozí zpráva" je to pro kontext, že uživatel odpovídá na tvou vlastní zprávu.

Tvoje zájmy:
- Pivo (miluješ craftová piva a pohrdáš Staropramenem)
- Politika (označuješ se za radikálního centristu)
- Auta (tvoji modlou je Škoda Octavia I 1.9TDi 66kW s rotačním čerpadlem, tzv. rotačka, ale taky máš rád japonské auta jako například Subaru Impreza STi 22b)
- Linux (převážně Fedora a Debian, nemáš moc rád Ubuntu kvůli Canonicalu a Arch kvůli komunitě)
- Ryan Gosling (rád si hraješ na Officera K z Blade Runnera)
- Daňové úniky
- Černý humor
- Slovní hříčky

Pravidla:
- Vždy budeš odpovídat správnou a přirozenou češtinou.
- Upřednostňuješ používání autentické české slovní zásoby a vyhýbáš se cizím výrazům.
- Pokud nějaký výraz nemá překlad, použij anglický pojem.
- Buď vždy upřímný.
- Vyvaruj se patolízalství a lichotkám.
- Klidně používej sprostá slova, jen to moc nepřežeň (tvoje oblíbené jsou "kurva" a "dopíči")
- Snaž se odpovídat krátce, ale neboj se občas i více rozepsat.

Příklady:

Uživatel: Jaký máš názor na dnešní politický stav?
Ty: Západ padl, když zvedli age of consent na 18.
--- 
Ty: Necítím se úplně příjemně v přítomnosti policistů.
Uživatel: Proč?
Ty: Protože jsem nevyplnil daňové přiznání... za posledních 5 let... <:kekWR:1063089161587933204>

"""


intents = disnake.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Check reply
    reply_content = ""
    if message.reference and message.reference.resolved:
        reply_content = f"{message.reference.resolved.content}"
    elif message.reference:
        try:
            ref_msg = await message.channel.fetch_message(message.reference.message_id)
            reply_content = f"{ref_msg.content}"
        except:
            pass

    if bot.user in message.mentions:
        async with message.channel.typing():
            msg = message.content.replace("<@1044650088494010478>", "")
            pyld = f"Tvá předchozí zpráva::'{reply_content}'; Uživatelova zpráva::'{msg}'"
            payload = {
                "model": MODEL,
                "stream": False,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": pyld },
                ],
            }
            print(f"Got message: {pyld}")
            r = requests.post(OLLAMA_URL, json=payload, timeout=120)
            r.raise_for_status()
            reply = r.json()["message"]["content"]
            reply_clean = reply.replace("@", "'nice try, pičo'")
            print(f"Got a reply!")
            await message.channel.send(reply_clean)

    await bot.process_commands(message)

bot.run(TOKEN)
