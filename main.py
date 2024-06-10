import nextcord 
# import math
# import asyncio
from nextcord.ext import commands
import requests
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





@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.slash_command(description="My first slash command", guild_ids=[guildID])
async def hello(interaction: nextcord.Interaction):
    await interaction.send("Hello!")
    await interaction.send(f"{interaction.user.name}")

@bot.slash_command(name= 'status', guild_ids=[guildID])
async def status(interaction: nextcord.Interaction, ctf_name: str):
    if ctf_name in db.list_collection_names():
        q = clientHu['Task-Manager'][f"{ctf_name}"].find({"Solved by": {"$exists": True}})
        await interaction.send(f"The status of {ctf_name} is: \n")
        for i in q:
            await interaction.send(f"{i['name']} : {i['Solved by']}")
    else:
        await interaction.send("No such CTF Exists, list to view")


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
                clientHu['Task-Manager'][f'{ctf_name}'].insert_one({"num": "1", "player" : None})
                
                await interaction.send(f"All challenges fetched successfully from {api_url}")

        else:
            await interaction.send(f"Failed to fetch challenges (status code {resp.status_code})")
    except Exception as e:
            print(e)
            await interaction.send(f"Error fetching challenges: {e}")

@bot.slash_command(name="done", guild_ids=[guildID])
async def done(interaction: nextcord.Interaction, ctf_name: str, challenge_name: str, flag: str):
    
    if ctf_name in db.list_collection_names():
        record = clientHu['Task-Manager'][f'{ctf_name}'].find_one({"name": challenge_name})
        if record == None:
            await interaction.send("Invalid challenge name.")
            return
        else:
            post = {"flag" : f"{flag}", "Solved by": f"{interaction.user.name}"}
            print(interaction.user.name)
            clientHu['Task-Manager'][f'{ctf_name}'].update_one({'name': f'{challenge_name}'}, {"$set": post}, upsert=False)
            playername = clientHu['Task-Manager'][f'{ctf_name}'].find_one({f'{interaction.user.id}': f'{interaction.user.name}'})
            if playername == None:
                clientHu['Task-Manager'][f'{ctf_name}'].update_one({"num": "1"}, {"$push" : {"player": f'{interaction.user.name}'}})
            await interaction.send(f"`{challenge_name}` has been solved by <@{interaction.user.id}>")
    else:
        await interaction.send("No such ctf")

    
    

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

# ---------------------------TASK MODULE STARTS HERE ------------------------------------------


members_task = {}

@bot.event
async def select_task(interaction: nextcord.Interaction,assigner_id:str,user_id:str):
    task_options=[nextcord.SelectOption(label= task ,value= task ) for task in members_task[user_id][assigner_id]]
    async def handle_task(interaction: nextcord.Interaction):
        task=interaction.data["values"][0]
        await interaction.response.send_message("uploaded and pinged")
        guild = bot.get_guild(int(id))
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
    guild = bot.get_guild(int(id))
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

@bot.slash_command(name="uploadtask", guild_ids=[guildID])
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

@bot.slash_command(name="taskdone", guild_ids=[guildID])
async def taskdone(interaction: nextcord.Interaction):
    user_id=str(interaction.user.id)
    if user_id in members_task:
        await dropdown_assigners_select(interaction,user_id)
    else:
        await interaction.response.send_message("```No Task For You```")

@bot.slash_command(name="showtask", guild_ids=[guildID])
async def showtask(interaction: nextcord.Interaction,role: nextcord.Role = None, member: nextcord.Member = None):
    guild = bot.get_guild(int(id))
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


bot.run(TOKEN)