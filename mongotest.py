import nextcord 
import math
import asyncio
from nextcord.ext import commands
import requests
import pandas as pd
from tabulate import tabulate
from config import TOKEN, guildID, mongostring
from pymongo import MongoClient
from pprint import pprint
intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

clientHu = MongoClient(mongostring)
print(clientHu)
db = clientHu['Task-Manager']


# challnames = clientHu['Task-Manager']['challenge_names']




@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.slash_command(description="My first slash command", guild_ids=[guildID])
async def hello(interaction: nextcord.Interaction):
    await interaction.send("Hello!")




@bot.slash_command(name= 'archive_ctf', guild_ids=[guildID])
async def archive_ctf(interaction: nextcord.Interaction, ctf_name: str):
    if ctf_name in db.list_collection_names():
        clientHu['Task-Manager'][f'{ctf_name}'].rename(ctf_name + " [Archived]", dropTarget = True)
        await interaction.send(f"{ctf_name} has been archived sucessfully.")
    else:
        await interaction.send("No such CTF Exists, list to view")


@bot.slash_command(name= 'list_all_ctfs ', guild_ids=[guildID])
async def ctf_list(interaction: nextcord.Interaction):
    await interaction.send('\n'.join(db.list_collection_names()))

@bot.slash_command(name="fetchchallenges", guild_ids=[guildID])
async def fetch_challenges(interaction: nextcord.Interaction,ctf_name: str, api_url : str):


    try:
        resp = requests.get(api_url)
        if resp.status_code ==200:
            resp_json = resp.json()
            if 'data' in resp_json:
                challengesinfo = resp_json['data']
                if isinstance(challengesinfo, list):
                    challenge_names_dict = [{'name': challenge['name']} for challenge in challengesinfo]
                clientHu['Task-Manager'][f'{ctf_name}'].insert_many(challenge_names_dict)
                await interaction.send(f"All challenges fetched successfully from {api_url}")

        else:
            await interaction.send(f"Failed to fetch challenges (status code {resp.status_code})")
    except Exception as e:
            print(e)
            await interaction.send(f"Error fetching challenges: {e}")      
@bot.slash_command(name="showflag", guild_ids=[guildID])
async def show_flag(interaction: nextcord.Interaction,ctf_name: str, challenge_name: str):

    record = clientHu['Task-Manager'][f'{ctf_name}'].find_one({"name": challenge_name})
    if record == None:
        await interaction.send("Invalid challenge name.")
        return

    else:
        if 'flag' in record:
            await interaction.send(f"The flag for `{record['name']}` is `{record['flag']}`")
        else:
            await interaction.send(f"Challenge `{record['name']}` has not been completed by anyone.")

bot.run(TOKEN)
