import nextcord
import math
import asyncio
from nextcord.ext import commands
import requests
import pandas as pd
from tabulate import tabulate
# import typing
intents = nextcord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix="!", intents=intents)
def chunks(df, chunk_size):
    return [df[i:i + chunk_size] for i in range(0, len(df), chunk_size)]
# api_url = 'https://jerseyctf.ctfd.io/api/v1/challenges'
guildID = 1217909401097080883
members_task = {}
# guildID = client.get_guild(int(id))
id="1217909401097080883"

fetched_challenges = []

completed_challenges = {}

@client.event
async def on_ready():
    print("Logged in")
async def select_task(interaction: nextcord.Interaction,assigner_id:str,user_id:str):
    task_options=[nextcord.SelectOption(label= task ,value= task ) for task in members_task[user_id][assigner_id]]
    async def handle_task(interaction: nextcord.Interaction):
        task=interaction.data["values"][0]
        await interaction.response.send_message("uploaded and pinged")
        guild = client.get_guild(int(id))
        assigner=guild.get_member(int(assigner_id))
        username=guild.get_member(int(user_id)).global_name
        (members_task[user_id][assigner_id]).remove(task)
        await assigner.send(username+" !task done "+task)
        if not members_task[user_id][assigner_id]:
            del members_task[user_id][assigner_id]
            if not members_task[user_id]:
                del members_task[user_id]
    dropdown = nextcord.ui.Select(
        placeholder="Choose task",  
        options=task_options,
        min_values=1,
        max_values=1)
    dropdown.callback=handle_task
    view = nextcord.ui.View()
    view.add_item(dropdown)
    await interaction.response.send_message("Choose task:", view=view,ephemeral=True)

async def dropdown_assigners_select(interaction: nextcord.Interaction,user_id:str):
    assigner_id_options=[]
    guild = client.get_guild(int(id))
    for assigner_id in members_task[user_id]:
        assigner_id_options.append(nextcord.SelectOption(label=(guild.get_member(int(assigner_id))).global_name, value=assigner_id))
    async def handle_assigner_id(interaction: nextcord.Interaction):
        assigner_id=interaction.data["values"][0]
        await select_task(interaction,assigner_id,user_id)
        view.stop()
    dropdown = nextcord.ui.Select(
        placeholder="Choose assigner name",  
        options=assigner_id_options,
        min_values=1,
        max_values=1)
    dropdown.callback=handle_assigner_id
    view = nextcord.ui.View()
    view.add_item(dropdown)
    await interaction.response.send_message("Choose assigner name:", view=view,ephemeral=True)

    
# async def dropdown_challenge_select(interaction: nextcord.Interaction,user_id:str):
#     # assigner_id_options=
#     guild = client.get_guild(int(id))
#     # for assigner_id in members_task[user_id]:
#     #     assigner_id_options.append(nextcord.SelectOption(label=(guild.get_member(int(assigner_id))).global_name, value=assigner_id))
#     async def handle_chall(interaction: nextcord.Interaction):
#         challenge_name=interaction.data["values"][0]
#     dropdown = nextcord.ui.Select(
#         placeholder="Choose challenge name",  
#         options=fetched_challenges,
#         min_values=1,
#         max_values=1)
#     dropdown.callback=handle_chall
#     view = nextcord.ui.View()
#     view.add_item(dropdown)
#     await interaction.response.send_message("Choose challenge name:", view=view,ephemeral=True)


@client.slash_command(name="uploadtask", guild_ids=[guildID])
async def uploadtask(interaction: nextcord.Interaction, task : str,role: nextcord.Role = None, member: nextcord.Member = None):
    user=interaction.user
    if role is None and member is None :
        await interaction.response.send_message("Club and Members Both cannot be empty Provide one")
        return
    if not(role is None or member is None) :
        await interaction.response.send_message("Provide one not both")
        return
    await interaction.response.send_message("Task uploaded and pinged")
    if member is None:
        for mem in role.members:
            try:
                await mem.send(user.global_name +" !task : "+task)
                if str(mem.id) not in members_task:
                    members_task[str(mem.id)]={str(user.id):[task]}
                else:
                    if str(user.id) not in members_task[str(mem.id)] :
                        members_task[str(mem.id)]={str(user.id):[task]}
                    elif task not in members_task[str(mem.id)][str(user.id)]:
                        members_task[str(mem.id)][str(user.id)].append(task)
            except : 
                continue
    else:
        await member.send(interaction.user.global_name +" !task : "+task)
        if str(member.id) not in members_task:
            members_task[str(member.id)]={str(user.id):[task]}
        else:
            if str(user.id) not in members_task[str(member.id)] :
                members_task[str(member.id)]={str(user.id):[task]}
            elif task not in members_task[str(member.id)][str(user.id)]:
                members_task[str(member.id)][str(user.id)].append(task)

@client.slash_command(name="taskdone", guild_ids=[guildID])
async def taskdone(interaction: nextcord.Interaction):
    user_id=str(interaction.user.id)
    if user_id in members_task:
        await dropdown_assigners_select(interaction,user_id)
    else:
        await interaction.response.send_message("```No Task For You```")

@client.slash_command(name="showtask", guild_ids=[guildID])
async def showtask(interaction: nextcord.Interaction,role: nextcord.Role = None, member: nextcord.Member = None):
    guild = client.get_guild(int(id))
    userid=interaction.user.id
    if not(role is None or member is None) :
        await interaction.response.send_message("```Provide one not both```") 
        return
    elif role is None and member is None:
        if str(userid) not in members_task:
            await interaction.response.send_message("```No Tasks for you```")
        else:
            message="** Tasks For You ** \n"
            for m_id , tasks in members_task[str(userid)].items():
                sender = (guild.get_member(int(m_id))).global_name
                message+="By "+sender+"\n"
                i = 1
                for task in tasks:
                    message+=str(i)+". "+task+"\n"
                    i+=1
            await interaction.response.send_message("```"+message+"```")
    elif role is None : 
        if str(member.id) not in members_task:
            await interaction.response.send_message(f"```No Tasks for {member.global_name}```")
        else :
            message=f"** Tasks for {member.global_name} **\n"
            for m_id , tasks in members_task[str(member.id)].items():
                sender = (guild.get_member(int(m_id))).global_name
                message+="By "+sender+"\n"
                i = 1
                for task in tasks:
                    message+=str(i)+". "+task+"\n"
                    i+=1
            await interaction.response.send_message("```"+message+"```")
    else:
        message=""
        for mem in role.members:
            if mem.global_name is None:
                continue
            elif str(mem.id) not in members_task:
                continue
            else: 
                message+=f"** Tasks for {mem.global_name} **\n"
                for m_id , tasks in members_task[str(mem.id)].items():
                    sender = (guild.get_member(int(m_id))).global_name
                    message+="By "+sender+"\n"
                    i = 1
                    for task in tasks:
                        message+=str(i)+". "+task+"\n"
                        i+=1
        if message=="":
            message="```No Task For Anyone Enjoy```"
        await interaction.response.send_message("```"+message+"```")


@client.slash_command(name="test", guild_ids=[guildID])
async def test(interaction: nextcord.Interaction):
    await interaction.channel.send("Hi")
    await interaction.response.send_message("yoooo")


@client.slash_command(name="test2", guild_ids=[guildID])
async def test2(ctx: nextcord.ApplicationCommandOption, name: str, time: int):
    print(str(name))
    await ctx.response.send_message(name)

@client.slash_command(name="fetchchallenges", guild_ids=[guildID])
async def fetch_challenges(ctx: nextcord.Interaction, api_url = str):
    global fetched_challenges 
    global challs
    if not fetched_challenges:   
        try:
            # api_url = url
            print(api_url)
            response = requests.get(api_url)
            if response.status_code == 200:
                challenges = response.json()['data']
                fetched_challenges = [challenge['name'] for challenge in challenges]  
                challs = [fetched_challenges]
                print(challs)
                global members
                members = []
                print(members)
                global lol
                lol = [""] * len(members)
                dict = {"Player": members, "Challenges Solved": lol,}
                global df
                df = pd.DataFrame(dict)
                df.set_index('Player', inplace=True)
                await ctx.response.send_message(f"All challenges fetched successfully from {api_url}")
                print(fetched_challenges)
            else:
                await ctx.response.send_message(f"Failed to fetch challenges (status code {response.status_code})")
        except Exception as e:
            print(e)
            await ctx.response.send_message(f"Error fetching challenges: {e}")
    else:
        await ctx.response.send_message(f"challenges already fetched from {api_url}")

@client.slash_command(name="done", guild_ids=[guildID])

async def done(interaction: nextcord.Interaction, challenge_name : str = nextcord.SlashOption(name="challenge_name", required=True, choices= fetched_challenges), flag = str):
    global fetched_challenges 
    global df
    # global lol
    if challenge_name not in fetched_challenges:
        await interaction.response.send_message("Invalid challenge name.")
        return

    completed_challenges[challenge_name] = flag
    print(challenge_name)
    # df.loc[f"{interaction.user}"]
    if interaction.user in members:
        if challenge_name in df.at[f"{interaction.user}",'Challenges Solved']:
            await interaction.response.send_message("Challenge already done by you.")
            return
        else:
            (df.at[f"{interaction.user}",'Challenges Solved']) += (challenge_name + "\n")
    else:
        df.loc[f"{interaction.user}"] = [f"{challenge_name}\n"]
        members.append(interaction.user)
    
    print(df)
    await interaction.response.send_message(f"Challenge '{challenge_name}' marked as completed by <@{interaction.user}>")
    

@client.slash_command(name="status", guild_ids=[guildID])
async def status(ctx: nextcord.ApplicationCommandOption):
    df_chunks = chunks(df, 5)
    for chunk in df_chunks:
        await ctx.channel.send(f"```{tabulate(chunk, headers='keys', tablefmt='psql')}```")
    print(fetched_challenges)
    await ctx.response.send_message("The Status is: ")

@client.slash_command(name="clearchall", guild_ids=[guildID])
async def clearchalls(ctx: nextcord.ApplicationCommandOption):
    global fetched_challenges
    fetched_challenges = []
    await ctx.response.send_message("All challenges cleared")

@client.slash_command(name="showflag", guild_ids=[guildID])
async def show_flag(ctx: nextcord.ApplicationCommandOption, challenge_name: str):
    global fetched_challenges

    if challenge_name not in fetched_challenges:
        await ctx.response.send_message("Invalid challenge name.")
        return

    if challenge_name in completed_challenges:
        flag = completed_challenges[challenge_name]
        await ctx.response.send_message(f"Flag for '{challenge_name}': `{flag}`")
    else:
        await ctx.response.send_message(f"Challenge '{challenge_name}' has not been completed by anyone.")

client.run(TOKEN)
