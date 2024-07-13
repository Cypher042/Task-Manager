import nextcord 
from nextcord.ext import commands
import os
from dotenv import load_dotenv
import requests
# from config import TOKEN, guildID, mongostring
from pymongo import MongoClient
import logging as log
from perms import perms


load_dotenv()

TOKEN = os.getenv('TOKEN')
guildID = int(os.getenv('guildID'))
mongostring = os.getenv('mongostring')


log.basicConfig(
    level=log.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="basic.log",
)




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

@bot.event
async def dropdown_ctf_name_select_status(interaction: nextcord.Interaction,user_id:str):
    ctf_names= db.list_collection_names()
    ctf_name_options=[nextcord.SelectOption(label= ctf_name ,value= ctf_name ) for ctf_name in ctf_names]
    async def handle_ctf_name_status(interaction: nextcord.Interaction):
        ctf_name_selected=interaction.data["values"][0]
        records = clientHu["Task-Manager"][f'{ctf_name_selected}'].find({'flags': {"$not": {"$size": 0}}})

        for record in records:


            print(record)
            c = record[list(record.keys())[1]]
            l = record[list(record.keys())[3]]
            embed = nextcord.Embed(title= f"{c}", color=0x0080ff)
            embed.set_author(name=f"Players who completed!")
            for i in l:
                key = list(i.keys())[0]
                embed.add_field(name=f"{i[f'{key}']}", value="", inline=False)
            await interaction.send(embed=embed)
    dropdown = nextcord.ui.Select(
        placeholder="Choose ctf name",
        options=ctf_name_options,
        min_values=1,
        max_values=1)
    dropdown.callback=handle_ctf_name_status
    view = nextcord.ui.View()
    view.add_item(dropdown)
    await interaction.response.send_message("Choose ctf name:", view=view,ephemeral=True)
@bot.slash_command(name="status", guild_ids=[guildID])
async def statusctf(interaction: nextcord.Interaction):
    member = interaction.guild.get_member(interaction.user.id) 
    if any(role.name in perms["status"] for role in member.roles):
        user_id=str(interaction.user.id)
        await dropdown_ctf_name_select_status(interaction,user_id)
    else:
        log.warning(f"{interaction.user.name} tried to use STATUS, No Permission")
        await interaction.send("No permission for that action!")


@bot.event
async def dropdown_ctf_name_select_archive(interaction: nextcord.Interaction,user_id:str):
    ctf_names= db.list_collection_names()
    ctf_name_options=[nextcord.SelectOption(label= ctf_name ,value= ctf_name ) for ctf_name in ctf_names]
    async def handle_ctf_name_archive(interaction: nextcord.Interaction):
        ctf_name_selected=interaction.data["values"][0]
        channel_name=ctf_name_selected
        category="ARCHIVE"
        guild = interaction.guild
        category = nextcord.utils.get(guild.categories, name=category)
        if guild:
            existing_channel = nextcord.utils.get(guild.channels, name=channel_name)
            if not existing_channel:
                await guild.create_text_channel(channel_name,category=category)
                channel = nextcord.utils.get(guild.channels, name=channel_name)

                await interaction.send("ARCHIVING ......")
                try: 
                    records = clientHu["Task-Manager"][f'{ctf_name_selected}'].find({'flags': {"$not": {"$size": 0}}})
                    for record in records:
                        print(record)
                        c = record['name']
                        l = record['flags']
                        embed = nextcord.Embed(title= f"{c}", color=0x0080ff)
                        embed.set_author(name=f"Flags")
                        for i in l:
                            key = list(i.keys())[0]
                            embed.add_field(name=f"{key}", value=f"{i[f'{key}']}", inline=False)
                        await channel.send(embed=embed)
                    for i in clientHu['Task-Manager'][f'{ctf_name_selected}'].distinct('category'):
                        print(i)
                        uncompleted = clientHu["Task-Manager"][f'{ctf_name_selected}'].find({"$and" : [{'category': i}, {'flags':  {"$size": 0}}]})
                        embed1=nextcord.Embed(title="Unfinished Challenges", color=0xfd0000)
                        embed1.set_author(name=f"{i}")
                        for record in uncompleted:
                            challs = record['name']
                            embed1.add_field(name=f"{challs}", value="", inline=False)
                        await channel.send(embed = embed1)
                    await interaction.channel.send(f"All challenges archived in `{channel_name}`")
                except Exception as e:
                    log.error(f"{interaction.user.name} tried to use Archive, encountered Error --> {e}")
                    await interaction.send(f"Could not Archive CTF. Error --> {e}")                        # await interaction.response.send_message(f'Channel {channel_name} created successfully!')
                db.drop_collection(ctf_name_selected)
            else:
                log.warning(f"{interaction.user.name} tried to archive {ctf_name_selected}, {channel_name} already exists! ")
                await interaction.response.send_message(f'Channel `{channel_name}` already exists!', ephemeral=True)
        else:
            await interaction.response.send_message('This command can only be used in a server.', ephemeral=True)
    dropdown = nextcord.ui.Select(
        placeholder="Choose ctf name",  
        options=ctf_name_options,
        min_values=1,
        max_values=1)
    dropdown.callback=handle_ctf_name_archive
    view = nextcord.ui.View()
    view.add_item(dropdown)
    await interaction.response.send_message("Choose ctf name:", view=view,ephemeral=True)
@bot.slash_command(name="archive_ctf", guild_ids=[guildID])
async def archivectf(interaction: nextcord.Interaction):
    member = interaction.guild.get_member(interaction.user.id) 
    if any(role.name in perms["archive_ctf"] for role in member.roles):
        user_id=str(interaction.user.id)
        await dropdown_ctf_name_select_archive(interaction,user_id)
    else:
        log.warning(f"{interaction.user.name} tried to use ARCHIVE, No Permission")
        await interaction.send("No permission for that action!")

@bot.slash_command(name= 'list_all_ctfs ', guild_ids=[guildID])
async def ctf_list(interaction: nextcord.Interaction):
   
    member = interaction.guild.get_member(interaction.user.id) 
    if any(role.name in perms["list_challenges"] for role in member.roles):
        embed=nextcord.Embed(title="All Ctfs", color=0x00df05)
        embed.add_field(name= '\n'.join(db.list_collection_names()),value="---------------------", inline=False)
        await interaction.send(embed=embed)

    else:
        log.warning(f"{interaction.user.name} tried to use List_all_Ctfs, No Permission")
        await interaction.send(f"No permission for that action!")



@bot.slash_command(name="fetch_challenges", guild_ids=[guildID])
async def fetch_challenges(interaction: nextcord.Interaction, ctf_name: str, api_url: str, api_token: str = None):
    member = interaction.guild.get_member(interaction.user.id)
    
    if any(role.name in perms["status"] for role in member.roles):

        try:
            headers = {}
            if api_token:
                headers = {
                    'Authorization': f'Token {api_token}',
                    'Content-Type': 'application/json'
                }

            resp = requests.get(api_url, headers=headers)
            if resp.status_code == 200:
                resp_json = resp.json()
                if 'data' in resp_json:
                    challengesinfo = resp_json['data']
                    if isinstance(challengesinfo, list):
                        await interaction.send(f"Fetching challs.... from {api_url}")
                        for challenge in challengesinfo:
                            if not clientHu["Task-Manager"][f'{ctf_name}'].find_one({'name': challenge['name']}):
                                challenge_data = {
                                    'name': challenge['name'],
                                    'category': challenge.get('category', 'Uncategorized'),
                                    'flags': []
                                }
                                clientHu["Task-Manager"][f'{ctf_name}'].insert_one(challenge_data)
                    await interaction.channel.send(f"All challenges stored from {api_url} at {ctf_name}")
                    log.info(f"{interaction.user.name} Fetchd Challenges from {api_url}, SUCCESS")
                    
                else:
                    await interaction.send(f"Response JSON does not contain 'data' field.")
                    log.error(f"{interaction.user.name} used Fetch! : Response JSON does not contain 'data' field.")
            else:
                await interaction.send(f"Failed to fetch challenges (status code {resp.status_code})")

        except Exception as e:
            print(e)
            log.error(f"{interaction.user.name} used Fetch. Encountered -->{e}")
            await interaction.send(f"Error fetching challenges: {e}")

    else:
        log.warning(f"{interaction.user.name} tried to use Fetch, No Permission")
        await interaction.send(f"No permission for that action!")



#-------------------------------------------ALTERNATE FETCH COMMANDS DO NOT DELETE CAN BE USEFUL--------------------------

# @bot.slash_command(name="fetchchallenges", guild_ids=[guildID])
# async def fetch_challenges(interaction: nextcord.Interaction, ctf_name: str, api_url: str, api_token: str = None):
#     member = interaction.guild.get_member(interaction.user.id)
    
#     if any(role.name in perms["status"] for role in member.roles):

#         try:
#             headers = {}
#             if api_token:
#                 headers = {
#                     'Authorization': f'Token {api_token}',
#                     'Content-Type': 'application/json'
#                 }

#             resp = requests.get(api_url, headers=headers)
#             if resp.status_code == 200:
#                 resp_json = resp.json()
#                 if 'data' in resp_json:
#                     challengesinfo = resp_json['data']
#                     if isinstance(challengesinfo, list):
#                         challenge_names_dict = [{'name': challenge['name'], 'category': challenge['category'], 'flags': []} for challenge in challengesinfo]
#                         clientHu['Task-Manager'][f'{ctf_name}'].insert_many(challenge_names_dict)
#                         clientHu['Task-Manager'][f'{ctf_name}'].insert_one({"num": "1", "player": None})
                    
#                     await interaction.send(f"All challenges fetched successfully from {api_url}")
#                 else:
#                     await interaction.send(f"Response JSON does not contain 'data' field.")
#             else:
#                 await interaction.send(f"Failed to fetch challenges (status code {resp.status_code})")

#         except Exception as e:
#             print(e)
#             await interaction.send(f"Error fetching challenges: {e}")

#     else:
#         await interaction.send(f"No permission for that action!")


# @bot.slash_command(name="fetchchallenges", guild_ids=[guildID])
# async def fetch_challenges(interaction: nextcord.Interaction,ctf_name: str, api_url : str):
#     member = interaction.guild.get_member(interaction.user.id)
    
#     if any(role.name in perms["status"] for role in member.roles):

#         try:
#             resp = requests.get(api_url)
#             if resp.status_code ==200:
#                 resp_json = resp.json()
#                 if 'data' in resp_json:
#                     challengesinfo = resp_json['data']
#                     if isinstance(challengesinfo, list):
#                         challenge_names_dict = [{'name': challenge['name'],'category': challenge['category'], 'flags' : []} for challenge in challengesinfo]
#                         # challenge_category_dict = [{'category': challenge['category']} for challenge in challengesinfo]
#                         # challenge_cat_dict = [{'category' : challenge['category']}]
#                     await interaction.send(f"All challenges fetched successfully from {api_url}")
#                     print(challenge_names_dict)
#                     clientHu['Task-Manager'][f'{ctf_name}'].insert_many(challenge_names_dict)
#                     # clientHu['Task-Manager'][f'{ctf_name}'].insert_many(challenge_category_dict)
#                     # clientHu['Task-Manager'][f'{ctf_name}'].insert_one({"num": "1", "player" : None})
#                     log.info(f"{interaction.user.name} Fetchd Challenges from {api_url}, SUCCESS")

#             else:
#                 log.error(f"{interaction.user.name} used Fetch! Failed to fetch challenges (status code {resp.status_code})")
#                 await interaction.send(f"Failed to fetch challenges (status code {resp.status_code})")
#         except Exception as e:
#                 print(e)
#                 log.error(f"{e}")
#                 await interaction.send(f"Error fetching challenges: {e}")
#     else:
#         log.warning(f"{interaction.user.name} tried to use Fetch, No Permission")
#         await interaction.send(f"No permission for that action!")

# -------------------------------------------------------------------------------------------------------------------------------------

@bot.event
async def select_chall_show(interaction: nextcord.Interaction,ctf_name_selected:str,category_name_selected:str,user_id:str):
    docs = clientHu['Task-Manager'][f'{ctf_name_selected}'].find({'category': category_name_selected}, {'name': 1, '_id': 0})
    challs= [doc['name'] for doc in docs if 'name' in doc]
    chall_options=[nextcord.SelectOption(label= chall ,value= chall ) for chall in challs]
    async def handle_chall_show(interaction: nextcord.Interaction):
        challenge_name=interaction.data["values"][0]
        ##yo bhai

        record = clientHu["Task-Manager"][f'{ctf_name_selected}'].find_one({"name": challenge_name})
        l = record['flags']
        embed = nextcord.Embed(title= f"{challenge_name}", color=0x0080ff)
        embed.set_author(name=f"Flags")
        for i in l:
            key = list(i.keys())[0]
            # print(i.keys())
            embed.add_field(name=f"{key}", value=f"{i[f'{key}']}", inline=False)
            
        await interaction.send(embed=embed, ephemeral=True)
        log.info(f"{interaction.user.name} used show_flag for {ctf_name_selected} - {challenge_name}")

    dropdown = nextcord.ui.Select(
        placeholder="Choose chall",  
        options=chall_options,
        min_values=1,
        max_values=1)
    dropdown.callback=handle_chall_show
    view = nextcord.ui.View()
    view.add_item(dropdown)
    await interaction.response.edit_message(content="Choose chall:", view=view)
  
async def select_category_show(interaction: nextcord.Interaction,ctf_name_selected:str,user_id:str):
    category_names= clientHu['Task-Manager'][f'{ctf_name_selected}'].distinct('category')
    category_name_options=[nextcord.SelectOption(label= category_name ,value= category_name ) for category_name in category_names]
    async def handle_category_name_show(interaction: nextcord.Interaction):
        category_name_selected=interaction.data["values"][0]
        await select_chall_show(interaction,ctf_name_selected,category_name_selected,user_id)
        view.stop()
    dropdown = nextcord.ui.Select(
        placeholder="Choose category name",  
        options=category_name_options,
        min_values=1,
        max_values=1)
    dropdown.callback=handle_category_name_show
    view = nextcord.ui.View()
    view.add_item(dropdown)
    await interaction.response.edit_message(content="Choose category name:", view=view)

async def dropdown_ctf_name_select_show(interaction: nextcord.Interaction,user_id:str):
    ctf_names= db.list_collection_names()
    ctf_name_options=[nextcord.SelectOption(label= ctf_name ,value= ctf_name ) for ctf_name in ctf_names]
    async def handle_ctf_name_show(interaction: nextcord.Interaction):
        ctf_name_selected=interaction.data["values"][0]
        await select_category_show(interaction,ctf_name_selected,user_id)
        view.stop()
    dropdown = nextcord.ui.Select(
        placeholder="Choose ctf name",  
        options=ctf_name_options,
        min_values=1,
        max_values=1)
    dropdown.callback=handle_ctf_name_show
    view = nextcord.ui.View()
    view.add_item(dropdown)
    await interaction.response.send_message("Choose ctf name:", view=view,ephemeral=True)


@bot.slash_command(name="show_flag", guild_ids=[guildID])
async def show_flag(interaction: nextcord.Interaction):
    member = interaction.guild.get_member(interaction.user.id) 
    if any(role.name in perms["show_flag"] for role in member.roles):
        user_id=str(interaction.user.id)
        await dropdown_ctf_name_select_show(interaction,user_id)
    else:
        log.warning(f"{interaction.user.name} tried to use Show_Flag, No Permission")
        await interaction.send("No permission for that action!")



# ---------------------------TASK MODULE STARTS HERE ------------------------------------------


members_task = {}    # Hail this dict, bros handling it all

@bot.event
async def select_chall(interaction: nextcord.Interaction,ctf_name_selected:str,category_name_selected:str,flag:str,user_id:str):
    docs = clientHu['Task-Manager'][f'{ctf_name_selected}'].find({'category': category_name_selected}, {'name': 1, '_id': 0})
    challs= [doc['name'] for doc in docs if 'name' in doc]
    chall_options=[nextcord.SelectOption(label= chall ,value= chall ) for chall in challs]
    async def handle_chall(interaction: nextcord.Interaction):
        challenge_name=interaction.data["values"][0]

        post = {f'{flag}': f'{interaction.user.name}'}
        print(interaction.user.name)

        clientHu['Task-Manager'][f'{ctf_name_selected}'].update_one({'name': f'{challenge_name}'}, {"$push" : {"flags": post}}, upsert=False)
    
        await interaction.send(f"`{challenge_name}` has been solved by <@{interaction.user.id}>")
        
    dropdown = nextcord.ui.Select(
        placeholder="Choose chall",  
        options=chall_options,
        min_values=1,
        max_values=1)
    dropdown.callback=handle_chall
    view = nextcord.ui.View()
    view.add_item(dropdown)
    await interaction.response.edit_message(content="Choose chall:", view=view)

async def select_category(interaction: nextcord.Interaction,ctf_name_selected:str,flag:str,user_id:str):
    category_names= clientHu['Task-Manager'][f'{ctf_name_selected}'].distinct('category')
    category_name_options=[nextcord.SelectOption(label= category_name ,value= category_name ) for category_name in category_names]
    async def handle_category_name(interaction: nextcord.Interaction):
        category_name_selected=interaction.data["values"][0]
        await select_chall(interaction,ctf_name_selected,category_name_selected,flag,user_id)
        view.stop()
    dropdown = nextcord.ui.Select(
        placeholder="Choose category name",  
        options=category_name_options,
        min_values=1,
        max_values=1)
    dropdown.callback=handle_category_name
    view = nextcord.ui.View()
    view.add_item(dropdown)
    await interaction.response.edit_message(content="Choose category name:", view=view)

async def dropdown_ctf_name_select(interaction: nextcord.Interaction,flag:str,user_id:str):
    ctf_names= db.list_collection_names()
    ctf_name_options=[nextcord.SelectOption(label= ctf_name ,value= ctf_name ) for ctf_name in ctf_names]
    async def handle_ctf_name(interaction: nextcord.Interaction):
        ctf_name_selected=interaction.data["values"][0]
        await select_category(interaction,ctf_name_selected,flag,user_id)
        view.stop()
    dropdown = nextcord.ui.Select(
        placeholder="Choose ctf name",  
        options=ctf_name_options,
        min_values=1,
        max_values=1)
    dropdown.callback=handle_ctf_name
    view = nextcord.ui.View()
    view.add_item(dropdown)
    await interaction.response.send_message("Choose ctf name:", view=view,ephemeral=True)

@bot.slash_command(name="submit_flag", guild_ids=[guildID])
async def submit_flag(interaction: nextcord.Interaction, flag : str):
    
    member = interaction.guild.get_member(interaction.user.id) 
    if any(role.name in perms["submit_flag"] for role in member.roles):
        user_id=str(interaction.user.id)
        await dropdown_ctf_name_select(interaction,flag,user_id)
    else:
        log.warning(f"{interaction.user.name} tried to use Submit Flag, No Permission")
        await interaction.send("No permission for that action!")

@bot.event
async def select_task(interaction: nextcord.Interaction,assigner_id:str,user_id:str):
    task_options=[nextcord.SelectOption(label= task ,value= task ) for task in members_task[user_id][assigner_id]]
    async def handle_task(interaction: nextcord.Interaction):
        task=interaction.data["values"][0]
        await interaction.response.send_message("uploaded and pinged")
        guild = bot.get_guild(guildID)
        assigner=guild.get_member(int(assigner_id))
        username=guild.get_member(int(user_id)).global_name
        (members_task[user_id][assigner_id]).remove(task)
        await assigner.send("```"+username +" : Task Done\nTask : "+task+"```")
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
    await interaction.response.edit_message(content="Choose task:", view=view)

async def dropdown_assigners_select(interaction: nextcord.Interaction,user_id:str):
    assigner_id_options=[]
    guild = bot.get_guild(guildID)
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
    await interaction.response.send_message("Choose assigner name:", view=view, ephemeral= True)

@bot.slash_command(name="uploadtask", guild_ids=[guildID])
async def uploadtask(interaction: nextcord.Interaction, task : str,role: nextcord.Role = None, member: nextcord.Member = None):
    member1 = interaction.guild.get_member(interaction.user.id) 
    if any(role.name in perms["uploadtask"] for role in member1.roles):
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
                    await mem.send("```"+user.global_name +" : You have a task to do\nTask : "+task+"```")
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
            await member.send("```"+interaction.user.global_name +" : You have a task to do\nTask : "+task+"```")
            if str(member.id) not in members_task:
                members_task[str(member.id)]={str(user.id):[task]}
            else:
                if str(user.id) not in members_task[str(member.id)] :
                    members_task[str(member.id)]={str(user.id):[task]}
                elif task not in members_task[str(member.id)][str(user.id)]:
                    members_task[str(member.id)][str(user.id)].append(task)
    else:
        log.warning(f"{interaction.user.name} tried to use Upload Task, No Permission")
        await interaction.send("No permission for that action!")


@bot.slash_command(name="taskdone", guild_ids=[guildID])
async def taskdone(interaction: nextcord.Interaction):
    member = interaction.guild.get_member(interaction.user.id) 
    if any(role.name in perms["taskdone"] for role in member.roles):
        user_id=str(interaction.user.id)
        if user_id in members_task:
            await dropdown_assigners_select(interaction,user_id)
        else:
            await interaction.response.send_message("```No Task For You```")
    else:
        await interaction.send("No permission for that action!")
        
        
@bot.slash_command(name="showtask", guild_ids=[guildID])
async def showtask(interaction: nextcord.Interaction,role: nextcord.Role = None, member: nextcord.Member = None):
    member1 = interaction.guild.get_member(interaction.user.id) 
    if any(role.name in perms["showtask"] for role in member1.roles):    
        guild = bot.get_guild(guildID)
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
    else:
        log.warning(f"{interaction.user.name} tried to use ShowTask, No Permission")
        await interaction.send("No permission for that action")        


bot.run(TOKEN)
