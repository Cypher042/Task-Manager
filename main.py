import discord
from discord.ext import commands

intents = discord.Intents.default()  
client = commands.Bot(command_prefix='/', intents=intents) 

@client.event
async def on_ready():
    print("The bot is ready for use")
    print("........................")

@client.command()
async def hello(ctx):
    await ctx.send("Hello, I am the Task Manager bot")


client.run("MTIyMjQ0NjE0MTI3NTI0MjUyNw.Gym1fl.BfJ1v6GLGTrIBabE9sBEwlZgegfR8FgOo8WLL0")                          

                      