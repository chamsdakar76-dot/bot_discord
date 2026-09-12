import discord
from discord.ext import commands
import json
import random
import asyncio
import os
import aiosqlite
import math
import sqlite3 as squilit
from typing import Literal, Any

#========= FUNCTIONS =========
async def read_json(file_name):
    with open(os.path.join(cur_folder,file_name),"r") as f:
        result = json.load(f)
    return result
async def write_in_json(file_name,new_content):
    with open(os.path.join(cur_folder,file_name),"w") as f:
        json.dump(new_content,f)
async def tell_admin_he_made_a_mistake(mistake:str):
    if mistake == "setleveling_by_games":
        pass
async def find_key_words(Message:str, msg:str):
    if msg is not None:
        pass
    else:
        msg_list = msg.split()
        winner_index = msg_list.index("winner_username")
        loser_index = None
        game_index = None
        loser_index = msg_list.index("loser_username")
        game_index = msg_list.index("game_name")
        msg_no_key = msg.replace("winner_username"," ")
        msg_no_key = msg_no_key.replace("loser_username"," ")
        msg_no_key = msg_no_key.replace("game_name"," ")
        msg_no_key = msg_no_key.split()
        Message_list = Message.split()
        Message_list_copy = Message_list.copy()
        winner_username = "N/A"
        loser_username = "N/A"
        finished_game_name = "N/A"
        for word in Message_list:
            if Message_list.count(word) == 1:
                if not word in msg_no_key:
                    if Message_list.index(word) == winner_index:
                        winner_username = word
                    elif Message_list.index(word) == loser_index:
                        loser_username = word
                    elif Message_list.index(word) == game_index:
                        finished_game_name = word
                    else:
                        await tell_admin_he_made_a_mistake("setleveling_by_games")
            elif Message_list.count(word) > 1:
                if Message_list_copy.index(word) == winner_index or Message_list_copy.index(word) == loser_index or Message_list_copy.index(word) == game_index:
                    if Message_list_copy.index(word) == winner_index:
                        winner_username = word
                        key_word_index = Message_list_copy.index(word)
                        Message_list_copy[key_word_index] = " _ - _ "
                    elif Message_list_copy.index(word) == loser_index:
                        loser_username = word
                        key_word_index = Message_list_copy.index(word)
                        Message_list_copy[key_word_index] = " _ - _ "
                    else:
                        finished_game_name = word
                        key_word_index = Message_list_copy.index(word)
                        Message_list_copy[key_word_index] = " _ - _ "
                else:
                    sus_word_index = Message_list_copy.index(word)
                    Message_list_copy[sus_word_index] = " _ - _ "
    return winner_username,loser_username,finished_game_name
def arrange_dict(dict_:dict[Any,float]):
    dict_ = dict(sorted(dict_.items(),key=lambda x : x[1]))
    return dict_
def digitkey_to_floatkey(dict_:dict,big_int_key:bool):
    dict_copy = dict_.copy()
    for key,value in dict_copy.items():
        if key.isdigit():
            del dict_[key]
            if not big_int_key:
                key = float(key)
            else:
                key = int(key)
            dict_[key] = value
    return dict_

#========= SETUP (Files,Token,Bot,On_ready) =========
cur_folder = os.path.dirname(__file__)

connection = squilit.connect(os.path.join(cur_folder,"data_bot.db"))
cursor = connection.cursor()
cursor.executescript("""CREATE TABLE IF NOT EXISTS welcome_settings(guild_id INTEGER PRIMARY KEY,
                                                               enabled INTEGER,
                                                               channel_id INTEGER,
                                                               welcome_mess TEXT);
            CREATE TABLE IF NOT EXISTS leveling_games_settings(guild_id INTEGER PRIMARY KEY,
                                                                enabled INTEGER,
                                                                game_bot_id INTEGER,
                                                                message_form TEXT,
                                                                game_name TEXT,
                                                                command_user_id INTEGER,
                                                                winner_N_A INTEGER,
                                                                loser_N_A INTEGER,
                                                                game_N_A INTEGER,
                                                                game_s_prefix_command TEXT,
                                                                game_type TEXT);
            CREATE TABLE IF NOT EXISTS games_xp_gains_settings(guild_id INTEGER PRIMARY KEY,
                                                                game_bot_id INTEGER,
                                                                game_name TEXT,
                                                                ELO_enabled INTEGER,
                                                                default_xp_gains INTEGER,
                                                                xp_lose INTEGER);
            CREATE TABLE IF NOT EXISTS invite_points(guild_id INTEGER,
                                                    user_id INTEGER,
                                                    points INTEGER DEFAULT 0,
                                                    PRIMARY KEY (guild_id, user_id));
            CREATE TABLE IF NOT EXISTS spin_points(guild_id INTEGER PRIMARY KEY,
                                                    legendary_spin_points INTEGER DEFAULT 2,
                                                    normal_spin_points INTEGER DEFAULT 1,
                                                    command_user TEXT)""")
connection.commit()
#empty variables have "NULL" as a value in db files

with open(os.path.join(cur_folder,"keys.json"),"r") as f:
    keys = json.load(f)
TOKEN = keys["Bot_Token"]
Intents = discord.Intents.default()
Intents.members = True
Intents.message_content = True
bot = commands.Bot(command_prefix="!",intents=Intents)

invites_data = {}
@bot.event
async def on_ready():
    for guild in bot.guilds:
        print(f"syncing to: {guild.name}")
        synced = await bot.tree.sync()
        print(f"synced {len(synced)} commands")
        invites_data[guild.id] = await guild.invites()
    print("Bot connected succesfully")

#========= SLASH COMMANDS =========
@bot.tree.command(name="set_points_for_spins",description="enter points needed for a normal spin and a legendary one")
@discord.app_commands.checks.has_permissions(administrator=True)
async def set_points_for_spins(interraction:discord.Interaction,points_for_normal_spin:int,points_for_legendary_spin:int):
    if not isinstance(points_for_legendary_spin,int) or not isinstance(points_for_normal_spin,int):
        await interraction.response.send_message("You should enter numbers !!!")
        return
    async with aiosqlite.connect(os.path.join(cur_folder,"data_bot.db")) as db:
        await db.execute("INSERT OR REPLACE INTO spin_points (guild_id,legendary_spin_points,normal_spin_points,command_user) VALUES (?,?,?,?)",(interraction.guild.id,points_for_legendary_spin,points_for_normal_spin,interraction.user.name))
        await db.commit()
    await interraction.response.send_message("DONE !")
    
@bot.tree.command(name="set_spin",description="enter names and their pourcentage in spin")
@discord.app_commands.checks.has_permissions(administrator=True)
async def set_spin(interraction:discord.Interaction,items_parameter:str):
    if not "=" in items_parameter or not "," in items_parameter or not ("1" in items_parameter or "2" in items_parameter or "3" in items_parameter or "4" in items_parameter or "5" in items_parameter or "6" in items_parameter or "7" in items_parameter or "8" in items_parameter or "9" in items_parameter):
        await interraction.response.send_message('pls enter it like a=0.7,b=0.2,c=0.1')
    else:
        spin_parameters = items_parameter.strip().replace(",","=").split("=")
        keys = []
        values = []
        total_value = 0
        for i in spin_parameters:
            if i.replace(".","0").isdigit():
                i = float(i)
                values.append(i)
                total_value += i
            else:
                keys.append(i)
        if not math.isclose(total_value,1):
            await interraction.response.send_message("the total pourcentages value should be 1 !")
        else:
            spin_parameters = dict(zip(keys,values))
            old_spin_parameters = await read_json("spin_parameters.json")
            old_spin_parameters = digitkey_to_floatkey(old_spin_parameters,True)
            old_spin_parameters[interraction.guild.id] = {interraction.user.name : spin_parameters}
            await write_in_json("spin_parameters.json",old_spin_parameters)
            await interraction.response.send_message("DONE !")

@bot.tree.command(name="set_legendary_spin",description="enter names and their pourcentage in spin")
@discord.app_commands.checks.has_permissions(administrator=True)
async def set_legendary_spin(interraction:discord.Interaction,items_parameter:str):
    if not "=" in items_parameter or not "," in items_parameter or not ("1" in items_parameter or "2" in items_parameter or "3" in items_parameter or "4" in items_parameter or "5" in items_parameter or "6" in items_parameter or "7" in items_parameter or "8" in items_parameter or "9" in items_parameter):
        await interraction.response.send_message('pls enter it like a=0.7,b=0.2,c=0.1')
    else:
        spin_parameters = items_parameter.strip().replace(",","=").split("=")
        keys = []
        values = []
        total_value = 0
        for i in spin_parameters:
            if i.replace(".","0").isdigit():
                i = float(i)
                values.append(i)
                total_value += i
            else:
                keys.append(i)
        if not math.isclose(total_value,1):
            await interraction.response.send_message("the total pourcentages value should be 1 !")
        else:
            spin_parameters = dict(zip(keys,values))
            old_spin_parameters = await read_json("legendary_spin_parameters.json")
            old_spin_parameters = digitkey_to_floatkey(old_spin_parameters,True)
            old_spin_parameters[interraction.guild.id] = {interraction.user.name : spin_parameters}
            await write_in_json("legendary_spin_parameters.json",old_spin_parameters)
            await interraction.response.send_message("DONE !")

@bot.tree.command(name="spin",description="normal spin for items set by admins")
async def spin(interraction : discord.Interaction):
    spin_parameters = await read_json("spin_parameters.json")
    spin_parameters = digitkey_to_floatkey(spin_parameters,True)
    async with aiosqlite.connect(os.path.join(cur_folder,"data_bot.db")) as db:
        cursor = await db.execute("SELECT normal_spin_points FROM spin_points WHERE guild_id = ?",(interraction.guild.id,))
        result = await cursor.fetchone()
    normal_points = result[0] if result is not None else 1
    if interraction.guild.id not in spin_parameters:
        await interraction.response.send_message("The admins didnt set items to spin !")
        return
    command_user = None
    for i in spin_parameters[interraction.guild.id].keys():
        command_user = i
    spin_parameters = spin_parameters[interraction.guild.id][command_user]
    async with aiosqlite.connect(os.path.join(cur_folder,"data_bot.db")) as db:
        cursor = await db.execute("SELECT points FROM invite_points WHERE (guild_id,user_id) = (?,?)",(interraction.guild.id,interraction.user.id))
        results = await cursor.fetchone()
    if results is None:
        user_points = 0
    else:
        user_points = results[0]
    if user_points < normal_points:
        await interraction.response.send_message("You dont have enough points ! You need at least 1 point for a spin and 2 points for a legendary one")
    else:
            spin_pourc = random.random()
            if spin_pourc == 1:
                spin_pourc -= 0.01
            elif spin_pourc == 0:
                spin_pourc += 0.01
            spin_resultes = []
            cumulative = 0
            spin_parameters = arrange_dict(spin_parameters)
            for thing, pourc in spin_parameters.items():
                cumulative += pourc
                if (spin_pourc < cumulative or math.isclose(spin_pourc,cumulative)) and spin_pourc > (cumulative - pourc):
                    spin_resultes.append(thing)
            if len(spin_resultes) > 1:
                spin_resulte = random.choice(spin_resultes)
            else:
                spin_resulte = spin_resultes[0]
            await interraction.response.send_message(f"Your spin resulte is {spin_resulte} !")
            async with aiosqlite.connect(os.path.join(cur_folder,"data_bot.db")) as db:
                await db.execute("INSERT OR REPLACE INTO invite_points (guild_id,user_id,points) VALUES (?,?,?)",(interraction.guild.id,interraction.user.id,user_points-normal_points))
                await db.commit()

@bot.tree.command(name="legendary_spin",description="legendary spin for items set by admins")
async def legendary_spin(interraction : discord.Interaction):
    spin_parameters = await read_json("legendary_spin_parameters.json")
    spin_parameters = digitkey_to_floatkey(spin_parameters,True)
    async with aiosqlite.connect(os.path.join(cur_folder,"data_bot.db")) as db:
        cursor = await db.execute("SELECT legendary_spin_points FROM spin_points WHERE guild_id = ?",(interraction.guild.id,))
        result = await cursor.fetchone()
    legendary_points = result[0] if result is not None else 2
    if interraction.guild.id not in spin_parameters:
        await interraction.response.send_message("The admins didnt set items to spin !")
        return
    command_user = None
    for i in spin_parameters[interraction.guild.id].keys():
        command_user = i
    spin_parameters = spin_parameters[interraction.guild.id][command_user]
    async with aiosqlite.connect(os.path.join(cur_folder,"data_bot.db")) as db:
        cursor = await db.execute("SELECT points FROM invite_points WHERE (guild_id,user_id) = (?,?)",(interraction.guild.id,interraction.user.id))
        results = await cursor.fetchone()
    if results is None:
        user_points = 0
    else:
        user_points = results[0]
    if user_points < legendary_points:
        await interraction.response.send_message("You dont have enough points ! You need at least 1 point for a spin and 2 points for a legendary one")
    else:
            spin_pourc = random.random()
            if spin_pourc == 1:
                spin_pourc -= 0.01
            elif spin_pourc == 0:
                spin_pourc += 0.01
            spin_resultes = []
            cumulative = 0
            spin_parameters = arrange_dict(spin_parameters)
            for thing, pourc in spin_parameters.items():
                cumulative += pourc
                if (spin_pourc < cumulative or math.isclose(spin_pourc,cumulative)) and spin_pourc > (cumulative - pourc):
                    spin_resultes.append(thing)
            if len(spin_resultes) > 1:
                spin_resulte = random.choice(spin_resultes)
            else:
                spin_resulte = spin_resultes[0]
            await interraction.response.send_message(f"Your spin resulte is {spin_resulte} !")
            async with aiosqlite.connect(os.path.join(cur_folder,"data_bot.db")) as db:
                await db.execute("INSERT OR REPLACE INTO invite_points (guild_id,user_id,points) VALUES (?,?,?)",(interraction.guild.id,interraction.user.id,user_points-legendary_points))
                await db.commit()

@bot.tree.command(name="last_one_set_spin_items",description="know who is the last admin who set spin items")
async def last_one_set_spin_items(interraction : discord.Interaction):
    spin_parameters = await read_json("spin_parameters.json")
    spin_parameters = digitkey_to_floatkey(spin_parameters,True)
    if interraction.guild.id not in spin_parameters:
        await interraction.response.send_message("no one set spin items in this server.")
    else:
        command_user = None
        for i in spin_parameters[interraction.guild.id].keys():
            command_user = i
        await interraction.response.send_message(f"Its {command_user} !")

@bot.tree.command(name="last_one_set_legendary_items",description="know who is the last admin who set spin items")
async def last_one_set_legendary_items(interraction : discord.Interaction):
    spin_parameters = await read_json("legendary_spin_parameters.json")
    spin_parameters = digitkey_to_floatkey(spin_parameters,True)
    if interraction.guild.id not in spin_parameters:
        await interraction.response.send_message("no one set legendary spin items in this server.")
    else:
        command_user = None
        for i in spin_parameters[interraction.guild.id].keys():
            command_user = i
        await interraction.response.send_message(f"Its {command_user} !")

@bot.tree.command(name="last_one_set_spin_points",description="know who is the last admin who set points needed for spins")
async def last_one_set_spin_points(interraction:discord.Interaction):
    async with aiosqlite.connect(os.path.join(cur_folder,"data_bot.db")) as db:
        cursor = await db.execute("SELECT command_user FROM spin_points WHERE guild_id = ?",(interraction.guild.id,))
        result = await cursor.fetchone()
    command_user = result[0]
    if command_user == "NULL" or command_user is None:
        await interraction.response.send_message("No one set points needed for spins in this server")
    else:
        await interraction.response.send_message(f"Its {command_user} !")

@bot.tree.command(name="setwelcome",description="set welcome channel&mesg |display_name=name|member.name=username|member.mention=mention")
@discord.app_commands.checks.has_permissions(administrator=True)
async def setwelcome(interraction : discord.Interaction, enabled : bool, channel : discord.TextChannel, welcome_message : str):
    if enabled == True:
        enabled = 1
    else:
        enabled = 0
    if channel.permissions_for(interraction.guild.me).send_messages != True:
        async with aiosqlite.connect(os.path.join(cur_folder,"data_bot.db")) as db:
            await db.execute("INSERT OR REPLACE INTO welcome_settings (guild_id, enabled, welcome_mess) VALUES (?,?,?)",(interraction.guild.id, enabled, welcome_message))
            await db.commit()
        await interraction.response.send_message("pls tape a text_channel that bot has permission to send messages in !")
    else:
        async with aiosqlite.connect(os.path.join(cur_folder,"data_bot.db")) as db:
            await db.execute("INSERT OR REPLACE INTO welcome_settings (guild_id, enabled, channel_id, welcome_mess) VALUES (?,?,?,?)",(interraction.guild.id, enabled, channel.id, welcome_message))
            await db.commit()
        await interraction.response.send_message("Done !")

@bot.tree.command(name="setleveling_by_games",description="not completed")
@discord.app_commands.checks.has_permissions(administrator=True)
async def setleveling_by_games(interraction : discord.Interaction, enabled : bool, game_bot : discord.Member, message_form : str, game_name : str, game_type : Literal["single_player(no_enemies)","multiplayer"]):
    await interraction.response.send_message("not completed yet")

@bot.tree.command(name="helpsetleveling_by_games",description="not completed")
@discord.app_commands.checks.has_permissions(administrator=True)
async def helpsetleveling_by_games(interraction : discord.Interaction):
    await interraction.response.send_message("_")

#========= EVENTS =========
on_join_locks = {}
@bot.event
async def on_member_join(member):
    if member.bot:
        return
    global invites_data
    global on_join_locks
    if member.guild.id not in on_join_locks:
        on_join_locks[member.guild.id] = asyncio.Lock()
    async with on_join_locks[member.guild.id]:
        invites = await member.guild.invites()
        missed_invites = []
        check_missed_invites = 0
        for invite in invites:
            member_used_link = 0
            inviter_id = None
            old_invite_now = None
            invite_missed = True
            for invite_data in invites_data[member.guild.id]:
                if invite_data.code == invite.code:
                    old_invite_now = invite_data
                elif check_missed_invites == 0:
                    invite_missed = True
                    for i in invites:
                        if invite_data.code == i.code:
                            invite_missed = False
                    if invite_missed:
                        missed_invites.append(invite_data)
            if old_invite_now is not None:
                if old_invite_now.inviter is not None:
                    inviter_id = old_invite_now.inviter.id
                    member_used_link = invite.uses - old_invite_now.uses
            elif missed_invites:
                for missed_invite in missed_invites:
                    if missed_invite.expires_at is not None :
                        now = discord.utils.utcnow()
                        if missed_invite.expires_at > now:
                            if missed_invite.max_uses > 0:
                                if missed_invite.uses == (missed_invite.max_uses - 1):
                                    if missed_invite.inviter is not None:
                                        inviter_id = missed_invite.inviter.id
                                        member_used_link = 1
                    else:
                        if missed_invite.max_uses > 0:
                            if missed_invite.uses == (missed_invite.max_uses - 1):
                                if missed_invite.inviter is not None:
                                    inviter_id = missed_invite.inviter.id
                                    member_used_link = 1
            if inviter_id is not None:
                if inviter_id != member.id and member_used_link != 0:
                    async with aiosqlite.connect(os.path.join(cur_folder,"data_bot.db")) as db:
                        cursor = await db.execute("SELECT points FROM invite_points WHERE (guild_id,user_id) = (?,?)",(member.guild.id,inviter_id))
                        resulte = await cursor.fetchone()
                    if resulte is None:
                        total_points = 1
                    else:
                        old_points = resulte[0]
                        total_points = old_points + 1
                    async with aiosqlite.connect(os.path.join(cur_folder,"data_bot.db")) as db:
                        await db.execute("INSERT OR REPLACE INTO invite_points (guild_id,user_id,points) VALUES (?,?,?)",(member.guild.id,inviter_id,total_points))
                        await db.commit()
            check_missed_invites = 1
        invites_data[member.guild.id] = invites
    async with aiosqlite.connect(os.path.join(cur_folder,"data_bot.db")) as db:
        cursor = await db.execute("SELECT enabled, channel_id, welcome_mess FROM welcome_settings WHERE guild_id = ?",(member.guild.id,))
        welcome_settings = await cursor.fetchone()
    if welcome_settings is not None:
        enabled, channel_id, message = welcome_settings
    else:
        enabled = 1
        channel_id = None
        message = None
    if enabled != 0:
        if channel_id is None:
            random_bot_text_channel = None
            text_channels = member.guild.text_channels
            if text_channels != None:
                for channel in text_channels:
                    if channel.permissions_for(member.guild.me).send_messages == True:
                        random_bot_text_channel = channel
                        break
            if random_bot_text_channel is not None:
                channel_id = random_bot_text_channel.id
        if message is None:
            message = f"{member.mention} Welcome {member.name} to {member.guild.name}"
        if channel_id is not None:
            if "member.display_name" in message:
                message = message.replace("member.display_name", f"{member.display_name}")
            if "member.name" in message:
                message = message.replace("member.name", f"{member.name}")
            if "member.mention" in message:
                message = message.replace("member.mention", f"{member.mention}")
            await member.guild.get_channel(channel_id).send(f"{message}")

@bot.event
async def on_message(message):
    if message.author.bot:
        if message.author != bot.user:
            async with aiosqlite.connect(os.path.join(cur_folder,"data_bot.db")) as db:
                pass

@bot.event
async def on_guild_join(guild):
    global invites_data
    invites_data[guild.id] = await guild.invites()
    print("joined a new server!!!!")
    if guild.system_channel:
        await guild.system_channel.send("Thanks for adding us in this server")













bot.run(TOKEN)
    