import discord
from discord.ext import commands
from discord import Interaction

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@client.event
async def on_ready():
    await client.change_presence(activity=discord.activity.Game(name = "Oraganizing Tasks"))
    print(f"{client.user.name} is logged in")

@client.command()
async def hi(ctx):
    await ctx.send("Hello :3!")

@client.tree.command()
async def ping(interaction : Interaction):
    bot_latency = round(client.latency*1000)
    await interaction.response.send_message(f"Pong!.. {bot_latency}")

client.run("MTIyMjQ1OTA3NDc2ODE0NjQ4Ng.GQ1ioF.YhEOI5IblkYXR18eYVOkL-WHuOIV3cQAeHONHA")