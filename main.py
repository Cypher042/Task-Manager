import nextcord
from nextcord.ext import commands
from nextcord import Interaction
import os
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


client.run(TOKEN)