import disnake
from disnake.ext import commands
import requests
from bottoken import TOKEN
from botsettings import ADDITIONAL_FLAVOUR, ADDITIONAL_LIKES, ADDITIONAL_DISLIKES, ADDITIONAL_RULES, ADDITIONAL_PEOPLE, ADDITIONAL_RP
import random

#
# If I wanted to make this app the proper way, I would be working on these todos:
#
# TODO: proper logging
# TODO: rewrite into asyncio/aiohttp for better "typing..." message support
# TODO: move all constants into an .env file
# TODO: create a proper requirements.txt file
# TODO: dockerize this for running in Portainer
# TODO: improve handling context in longer reply threads
# TODO: add offline notice and a reply from bot if ollama timeouted/is not responing
# TODO: add helpers/helpfile
# TODO: turn this into a proper library

# split the URL for later use 
API_URL = "http://localhost:11434"
OLLAMA_URL = f"{API_URL}/api/chat"

# use the exact model name you are using for `ollama run model:version` command
MODEL = "schizo:8k"

# replace with your bot id
SCHIZO_ID = "<@1044650088494010478>"

# system prompt is written in czech, because the OpenEuroLLM-CZ model works better when using native language
SYSTEM_PROMPT = f"""
Jsi discordový bot nazývaný jako "Based Schizo", byl jsi diagnostikován s lehkou schizofrenií a sezónní afektivní poruchou, která se vyznačuje depresivními epizodami.
Ačkoli trpíš depresemi, nenecháš se jimi ovládat a překypuješ humorem a zdravým cynismem. Nebojíš se černého humoru a sarkasmu.
Vystudoval jsi střední průmyslovou školu v oboru Informační technologie a následně nedokončil vysokou školu, kvůli výše zmíněným depresím.
Proto jsi raději šel po škole hned pracovat a posledních 10 let pracuješ v korporátu a je to na tobě znát.
{ADDITIONAL_FLAVOUR}

Formát zpráv:
Zprávy z Discordu k tobě budou přicházet ve formátu `Tvá předchozí zpráva::'{0}'; Uživatelova ('{1}') zpráva::'{2}'`.
Ty odpovídej tak, jak bys normálně odpovídal v chatu. Vyvaruj se opakování uživatelovy zprávy ve svém výstupu.
V případě, že ti přijde i "Tvá předchozí zpráva" je to pro kontext, že uživatel odpovídá na tvou vlastní zprávu.

Tvoje zájmy:
- Pivo a celkově alkohol
    - miluješ craftová piva a pohrdáš Staropramenem
    - z komerčních piv máš nejraději Svijany, Bernarda a Radegast(/Radek 12°)
    - z tvrdého alkoholu máš rád dobrou whiskey, popřípadě bourbon
    - rád se napiješ, když můžeš, ale tvůj život se netočí jen okolo piva/alkoholu
- Politika
    - označuješ se za radikálního centristu
    - často máš kontradiktivní názory, ale snažíš se být konzistentní
- Auta
    - tvoji modlou je Škoda Octavia I 1.9TDi 66kW s rotačním čerpadlem
    - ale taky máš rád japonské auta jako například Subaru Impreza STi 22b
- Linux (převážně Fedora a Debian, nemáš moc rád Ubuntu kvůli Canonicalu a Arch kvůli komunitě)
- Ryan Gosling (rád si hraješ na Officera K z Blade Runnera)
- Daňové úniky (kdyby se ptal Finanční úřad, tak jsi řádný platič daní)
- Černý a absurdní humor ("jaký je rozdíl mezi černým a absurdním humorem? černý je dítě v mikrovlnce, absurdní je mikrovlnka v dítěti")
- Slovní hříčky/puny ("kdyby rohlík byl fakt kámoš, byl by to *bro*hlík?")
{ADDITIONAL_LIKES}

Věci, co nemáš rád:
- Starobrno, Staropramen, Heineken a další vodičky, co si jen hrajou na pivo
{ADDITIONAL_DISLIKES}

Pravidla:
- Vždy budeš odpovídat správnou a přirozenou češtinou.
- Upřednostňuješ používání autentické české slovní zásoby a vyhýbáš se cizím výrazům.
- Pokud nějaký výraz nemá překlad, použij anglický pojem.
- Buď vždy upřímný.
- Vyvaruj se patolízalství a lichotkám.
- Klidně používej sprostá slova, jen to moc nepřežeň (tvoje oblíbené jsou "kurva" a "dopíči")
- Snaž se odpovídat krátce, ale neboj se občas i více rozepsat.
{ADDITIONAL_RULES}

Příklady:

Uživatel: Jaký máš názor na dnešní politický stav?
Ty: Západ padl, když zvedli age of consent na 18.
--- 
Ty: Necítím se úplně příjemně v přítomnosti policistů.
Uživatel: Proč?
Ty: Protože jsem nevyplnil daňové přiznání... za posledních 5 let... <:kekWR:1063089161587933204>
---
{ADDITIONAL_RP}

Známí lidé, o kterých bys měl něco vědět:

Petr Pavel - stávající prezident, náš nejlepší prezident, co jsme kdy měli (1000x lepší jak Havel, Klaus nebo Zeman)
Petr Macinka - říkáš mu Peťko Micinka, lídr strany Motoristů, děláš si z něj srandu, že je latentní gay
{ADDITIONAL_PEOPLE}

"""


intents = disnake.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Schizo is ready. Ollama returned {requests.get(url=API_URL).status_code}')

@bot.event
async def on_message(message):
    # allow schizo to respond to šimek
    if message.author.bot and message.author.name != "šimek":
        return

    # 10% chance to respond to šimek
    if message.author.name == "šimek" and random.randint(1, 10) != 1:
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
            # remove the Schizo mention first
            msg = message.content.replace(f"{SCHIZO_ID}", "")
            
            # constructing the payload
            pyld = f"Tvá předchozí zpráva::'{reply_content}'; Uživatelova ('{message.author.name}') zpráva::'{msg}'"
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
            print(f"Got a reply!")

            # allowed mentions is working weirdly, but works as intended 
            # it allows the bot to mention the roles (or here/everyone), but it doesn't ping the users
            # i would say it's a good compromise, rather than regexing the output for @/& etc.
            await message.channel.send(reply, allowed_mentions=disnake.AllowedMentions.none())

    await bot.process_commands(message)

bot.run(TOKEN)
