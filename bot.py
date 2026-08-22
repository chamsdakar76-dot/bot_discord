import discord
from discord.ext import commands
import json
import os
import aiosqlite
import sqlite3 as squilit
from typing import Literal

#========= FUNCTIONS =========
async def tell_admin_he_made_a_mistake(mistake:str):
    if mistake == "setleveling_by_games":
        pass
async def find_key_words(Message:str, msg:str, win_lose_only:int, win_only:int, win_game_only:int):
    if (win_only == win_lose_only and win_only == 1) or (win_game_only == win_only and win_only == 1) or (win_game_only == win_lose_only and win_lose_only == 1):
        pass
    else:
        msg_list = msg.split()
        winner_index = msg_list.index("winner_username")
        loser_index = None
        game_index = None
        if win_game_only == 0 and win_only == 0:
            loser_index = msg_list.index("loser_username")
        if win_only == 0 and win_lose_only == 0:
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

#========= SETUP (Files,Token,Bot,On_ready) =========
cur_folder = os.path.dirname(__file__)

connection = squilit.connect(os.path.join(cur_folder,"data_bot.db"))
cursor = connection.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS welcome_settings(guild_id INTEGER PRIMARY KEY,
                                                               enabled INTEGER,
                                                               channel_id INTEGER,
                                                               welcome_mess TEXT)
            CREATE TABLE IF NOT EXISTS leveling_games_settings(guild_id INTEGER PRIMARY KEY,
                                                                enabled INTEGER,
                                                                game_bot_id INTEGER,
                                                                message_form TEXT,
                                                                game_name TEXT,
                                                                command_user_id INTEGER,
                                                                winner_only INTEGER,
                                                                winner_loser_only INTEGER,
                                                                winner_game_only INTEGER,
                                                                game_type TEXT)
            CREATE TABLE IF NOT EXISTS games_xp_gains_settings(guild_id INTEGER PRIMARY KEY,
                                                                )""")
connection.commit()

with open(os.path.join(cur_folder,"keys.json"),"r") as f:
    keys = json.load(f)
TOKEN = keys["Bot_Token"]
Intents = discord.Intents.default()
Intents.members = True
Intents.message_content = True
bot = commands.Bot(command_prefix="!",intents=Intents)

@bot.event
async def on_ready():
    for guild in bot.guilds:
        print(f"syncing to: {guild.name}")
        synced = await bot.tree.sync()
        print(f"synced {len(synced)} commands")
    print("Bot connected succesfully")

#========= SLASH COMMANDS =========
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

@bot.tree.command(name="setleveling_by_games",description="set game_bot and his message_form and his games|Do /help'command_name' to know more")
@discord.app_commands.checks.has_permissions(administrator=True)
async def setleveling_by_games(interraction : discord.Interaction, enabled : bool, game_bot : discord.member, message_form : str, game_name : str, game_type : Literal["single_player(no_enemies)","multiplayer"]):
    if enabled == True:
        enabled = 1
    if enabled == False:
        enabled = 0
    if enabled == 1:
        if game_bot is not None:
            if "winner_username" in message_form:
                if "loser_username" in message_form and "game_name" in message_form:
                    winner_only = 0
                    winner_loser_only = 0
                    winner_game_only = 0
                elif "loser_username" in message_form:
                    winner_loser_only = 1
                    winner_only = 0
                    winner_game_only = 0
                elif "game_name" in message_form:
                    winner_game_only = 1
                    winner_only = 0
                    winner_loser_only = 0
                else:
                    winner_loser_only = 0
                    winner_only = 1
                    winner_game_only = 0
            else:
                interraction.response.send_message("There should be at least winner_username in message_form")
                async with aiosqlite.connect(os.path.join(cur_folder,"data_bot.db")) as db:
                    db.execute("INSERT OR REPLACE INTO leveling_games_settings (guild_id,enabled,game_bot_id,message_form,game_name,command_user_id,winner_only,winner_loser_only,winner_game_only,game_type) VALUES (?,?,?,?,?,?,?,?,?)",(interraction.guild.id,enabled,game_bot.id,message_form,game_name,interraction.user.id,winner_only,winner_loser_only,winner_game_only,game_type))
                    db.commit()
                interraction.response.send_message("Done")
        else:
            interraction.response.send_message("Pls set a bot that exists in your server")
    else:
        interraction.response.send_message("leveling by games disabled.")

@bot.tree.command(name="helpsetleveling_by_games",description="know really important things about /setleveling_by_games")
@discord.app_commands.checks.has_permissions(administrator=True)
async def helpsetleveling_by_games(interraction : discord.Interaction):
    interraction.response.send_message("""set a bot that exist in your server and that affords games , and set the form of his message that appears when the game is done and set the name of his games .
    in setting the form of the message dont forget these keys words :
    winner_name | loser_name | winner_username | loser_username | game""")

#========= EVENTS ==========
@bot.event
async def on_member_join(member):
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
            random_bot_text_channel : discord.TextChannel
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
                cursor = await db.execute("SELECT (enabled,game_bot_id,message_form,game_name,command_user_id,winner_only,winner_loser_only,winner_game_only,game_type) FROM leveling_games_settings WHERE guild_id = ?",(message.guild.id,))
                enabled,game_bot_id,message_form,game_name,command_user_id,winner_only,winner_loser_only,winner_game_only,game_type = await cursor.fetchone()
            if enabled == 1:
                if message.author.id == game_bot_id:
                    winner_username,loser_username,finished_game_name = await find_key_words(message,message_form,winner_loser_only,winner_only,winner_game_only)
                    if game_type == "single_player(no_enemies)" and loser_username != "N/A":
                        await tell_admin_he_made_a_mistake("setleveling_by_games")
                        game_type = "multiplayer"
                    #===== not completed =====










bot.run(TOKEN)


