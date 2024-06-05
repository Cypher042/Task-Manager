import nextcord
import math
import asyncio
from nextcord.ext import commands
import requests
import pandas as pd
from tabulate import tabulate
from config import TOKEN

intents = nextcord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.slash_command(description="My first slash command", guild_ids=[TESTING_GUILD_ID])
async def hello(interaction: nextcord.Interaction):
    await interaction.send("Hello!")


bot.run(TOKEN)