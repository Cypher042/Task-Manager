import nextcord
from nextcord.ext import commands
from nextcord import Interaction
import os
import pandas as pd
import requests
from tabulate import tabulate


def chunks(df, chunk_size):
    return [df[i:i + chunk_size] for i in range(0, len(df), chunk_size)]

fetched_challenges = []
completed_challenges = {}

api_url = 'https://jerseyctf.ctfd.io/api/v1/challenges'

intents=nextcord.Intents.default()
intents.members=True
client = commands.Bot(command_prefix="!", intents=intents)

@client.event
async def on_ready():
    print("logged in")

@client.slash_command(name = "test", guild_ids=[1217909401097080883])
async def test(interaction : Interaction):
    await interaction.response.send_message("hi")
    
@client.slash_command(name = "test2", guild_ids=[1217909401097080883])
async def test2(ctx, name: str,  time: int):
    print(str(name))
    await ctx.response.send_message(name)


@client.slash_command(name="fetchchallenges", guild_ids=[732912296136802304])
async def fetch_challenges(ctx: nextcord.ApplicationCommandOption):
    global fetched_challenges  # Marking fetched_challenges as global
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            challenges = response.json()['data']
            fetched_challenges = [challenge['name'] for challenge in challenges]  # Update fetched challenges list
            challsdf = pd.DataFrame(fetched_challenges)
            print(challsdf)
            df_chunks = chunks(challsdf, 5)
            for chunk in df_chunks:
                await ctx.channel.send(f"```{tabulate(chunk, headers='keys', tablefmt='psql')}```")
        else:
            await ctx.response.send_message(f"Failed to fetch challenges (status code {response.status_code})")
    except Exception as e:
        await ctx.response.send_message(f"Error fetching challenges: {e}")
@client.slash_command(name="done", guild_ids=[732912296136802304])
async def done(ctx: nextcord.ApplicationCommandOption, challenge_name: str, flag: str):
    global fetched_challenges  # Accessing fetched_challenges list
    if challenge_name not in fetched_challenges:
        await ctx.response.send_message("Invalid challenge name.")
        return

    # Store the completion status of the challenge 
    completed_challenges[challenge_name] = flag
    await ctx.response.send_message(f"Challenge '{challenge_name}' marked as completed by <@{ctx.user.id}>")

client.run(TOKEN)
