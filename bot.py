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
                                                    PRIMARY KEY (guild_id, user_id))""")
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
@bot.tree.command(name="spin",description="enter names and their pourcentage to spin")
async def spin(interraction : discord.Interaction,spin_parametres:str):
    async with aiosqlite.connect(os.path.join(cur_folder,"data_bot.db")) as db:
        cursor = await db.execute("SELECT points FROM invite_points WHERE (guild_id,user_id) = (?,?)",(interraction.guild.id,interraction.user.id))
        results = await cursor.fetchone()
    if results is None:
        user_points = 0
    else:
        user_points = results[0]
    if user_points < 1:
        await interraction.response.send_message("You dont have enough points ! You need at least 1 point for a spin and 2 points for a legendary one")
    else:
        if not "=" in spin_parametres or not "," in spin_parametres or not ("1" in spin_parametres or "2" in spin_parametres or "3" in spin_parametres or "4" in spin_parametres or "5" in spin_parametres or "6" in spin_parametres or "7" in spin_parametres or "8" in spin_parametres or "9" in spin_parametres):
            await interraction.response.send_message('pls enter it like a=0.7,b=0.2,c=0.1')
        else:
            spin_parametres = spin_parametres.strip().replace(",","=").split("=")
            keys = []
            values = []
            for i in spin_parametres:
                if i.replace(".","0").isdigit():
                    i = float(i)
                    values.append(i)
                else:
                    keys.append(i)
            spin_parametres = dict(zip(keys,values))
            while True:
                spin_pourc = random.random()
                if spin_pourc != 1 and spin_pourc != 0:
                    break
            spin_resultes = []
            cumulative = 0
            spin_parametres = arrange_dict(spin_parametres)
            for thing, pourc in spin_parametres.items():
                cumulative += pourc
                if (spin_pourc < cumulative or math.isclose(spin_pourc,cumulative)) and spin_pourc > (cumulative - pourc):
                    spin_resultes.append(thing)
            if len(spin_resultes) > 1:
                spin_resulte = random.choice(spin_resultes)
            else:
                spin_resulte = spin_resultes[0]
            await interraction.response.send_message(f"Your spin resulte is {spin_resulte} !")
            async with aiosqlite.connect(os.path.join(cur_folder,"data_bot.db")) as db:
                await db.execute("INSERT OR REPLACE INTO invite_points (guild_id,user_id,points) VALUES (?,?,?)",(interraction.guild.id,interraction.user.id,user_points-1))
                await db.commit()

@bot.tree.command(name="legendary_spin",description="enter names and their pourcentage to spin")
async def legendary_spin(interraction : discord.Interaction,spin_parametres:str):
    async with aiosqlite.connect(os.path.join(cur_folder,"data_bot.db")) as db:
        cursor = await db.execute("SELECT points FROM invite_points WHERE (guild_id,user_id) = (?,?)",(interraction.guild.id,interraction.user.id))
        results = await cursor.fetchone()
    if results is None:
        user_points = 0
    else:
        user_points = results[0]
    if user_points < 2:
        await interraction.response.send_message("You dont have enough points ! You need at least 1 point for a spin and 2 points for a legendary one")
    else:
        if not "=" in spin_parametres or not "," in spin_parametres or not ("1" in spin_parametres or "2" in spin_parametres or "3" in spin_parametres or "4" in spin_parametres or "5" in spin_parametres or "6" in spin_parametres or "7" in spin_parametres or "8" in spin_parametres or "9" in spin_parametres):
            await interraction.response.send_message('pls enter it like a=0.7,b=0.2,c=0.1')
        else:
            spin_parametres = spin_parametres.strip().replace(",","=").split("=")
            keys = []
            values = []
            for i in spin_parametres:
                if i.replace(".","0").isdigit():
                    i = float(i)
                    values.append(i)
                else:
                    keys.append(i)
            spin_parametres = dict(zip(keys,values))
            while True:
                spin_pourc = random.random()
                if spin_pourc != 1 and spin_pourc != 0:
                    break
            spin_resultes = []
            cumulative = 0
            spin_parametres = arrange_dict(spin_parametres)
            for thing, pourc in spin_parametres.items():
                cumulative += pourc
                if (spin_pourc < cumulative or math.isclose(spin_pourc,cumulative)) and spin_pourc > (cumulative - pourc):
                    spin_resultes.append(thing)
            if len(spin_resultes) > 1:
                spin_resulte = random.choice(spin_resultes)
            else:
                spin_resulte = spin_resultes[0]
            await interraction.response.send_message(f"Your spin resulte is {spin_resulte} !")
            async with aiosqlite.connect(os.path.join(cur_folder,"data_bot.db")) as db:
                await db.execute("INSERT OR REPLACE INTO invite_points (guild_id,user_id,points) VALUES (?,?,?)",(interraction.guild.id,interraction.user.id,user_points-2))
                await db.commit()

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
    