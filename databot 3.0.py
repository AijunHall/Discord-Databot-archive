from datetime import datetime
from datetime import timedelta
import os
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager
from matplotlib.ticker import MaxNLocator
import discord
from discord.ext import tasks, commands
from discord.utils import get
import mysql.connector

mydb = mysql.connector.connect(

    host = "localhost",
    user = "root",
    passwd = "",
    database = "databot"
)
mycursor = mydb.cursor(buffered=True)
sqlFormulaMessages = "INSERT INTO messages (message_id, user_id, server_id, channel_id, message_datetime, message_content) VALUES (%s, %s, %s, %s, %s, %s)"
sqlFormulaAttachments = "INSERT INTO attachments (message_id, user_id, server_id, channel_id, attachment_datetime, attachment_content) VALUES (%s, %s, %s, %s, %s, %s)"
sqlFormulaServers = "INSERT INTO servers (server_id, channel_count, user_count, message_count, attachment_count) VALUES (%s, %s, %s, %s, %s)"
sqlFormulaChannels = "INSERT INTO channels (channel_id, server_id, message_count, attachment_count) VALUES (%s, %s, %s, %s)"
sqlFormulaUsers = "INSERT INTO users (user_id, server_count, message_count, attachment_count) VALUES (%s, %s, %s, %s)"
print(mydb)

TOKEN = ""
COMMAND_PREFIX = ">>"
ACTIVITY_STATUS = f"もふもふ"

client = commands.Bot(command_prefix = COMMAND_PREFIX)
client.remove_command("help")

@tasks.loop(hours=6)
async def getdataloop(index=0):

    print(index)
    index += 1

    all_visible_guilds = client.guilds
    for guild in all_visible_guilds:

        guild_id = guild.id

        mycursor.execute(f"DELETE FROM servers WHERE server_id = {guild_id}")
        mycursor.execute(f"DELETE FROM messages WHERE server_id = {guild_id}")
        mycursor.execute(f"DELETE FROM attachments WHERE server_id = {guild_id}")
        mycursor.execute(f"DELETE FROM channels WHERE server_id = {guild_id}")

        input_guild = guild
        print(f"Reading [{input_guild.name}] history...\n")

        #First use enterServerHistory() to fill out messages and attachments tables
        channel_all_history = []
        for channel in input_guild.text_channels:
            try:
                print(f"Reading #{channel} message history...")
                channel_all_history += await channel.history(limit=None).flatten()
                print(f"Finished reading #{channel} message history\n")

            except discord.Forbidden:
                print(f"\nERROR: {channel.name} could not be read.\n")

        enterServerHistory(channel_all_history)
        print("Finished reading server history.\n")

        #Now fill servers table with the inputted server, using entered data from enterServerHistory()
        mycursor.execute(f"SELECT COUNT(DISTINCT channel_id) FROM messages WHERE server_id = {guild_id}")
        channel_count = mycursor.fetchone()[0]

        users_count = len(input_guild.members)

        mycursor.execute(f"SELECT COUNT(*) FROM messages WHERE server_id = {guild_id}")
        message_count = mycursor.fetchone()[0]

        mycursor.execute(f"SELECT COUNT(*) FROM attachments WHERE server_id = {guild_id}")
        attachment_count = mycursor.fetchone()[0]

        this_server = (guild_id, channel_count, users_count, message_count, attachment_count)
        mycursor.execute(sqlFormulaServers, this_server)

        #Now fill channels table with the inputted server, using entered data from enterServerHistory()
        mycursor.execute(f"SELECT DISTINCT channel_id FROM messages WHERE server_id = {guild_id}")
        channels_list = mycursor.fetchall()

        for channel in channels_list:
            channel_id = channel[0]

            mycursor.execute(f"SELECT COUNT(*) FROM messages WHERE channel_id = {channel_id}")
            channel_message_count = mycursor.fetchone()[0]

            mycursor.execute(f"SELECT COUNT(*) FROM attachments WHERE channel_id = {channel_id}")
            channel_attachment_count = mycursor.fetchone()[0]

            this_channel = (channel_id, guild_id, channel_message_count, channel_attachment_count)
            mycursor.execute(sqlFormulaChannels, this_channel)

        #Now fill users table with the inputted server, using entered data from enterServerHistory()
        mycursor.execute("SELECT DISTINCT user_id FROM users")
        all_known_unique_users = []

        for user_id in mycursor.fetchall():
            all_known_unique_users.append(user_id[0])

        all_known_unique_users = tuple(all_known_unique_users)

        mycursor.execute(f"SELECT DISTINCT user_id FROM messages WHERE server_id = {guild_id}")
        users_with_messages_list = mycursor.fetchall()

        mycursor.execute(f"SELECT DISTINCT user_id FROM attachments WHERE server_id = {guild_id}")
        users_with_attachments_list = mycursor.fetchall()

        all_new_unique_users = tuple(np.unique(users_with_messages_list + users_with_attachments_list))

        for user_id in all_new_unique_users:

            user_id = int(user_id)

            if (user_id not in all_known_unique_users):

                server_count = 1

                mycursor.execute(f"SELECT COUNT(*) FROM messages WHERE user_id = {user_id}")
                message_count = mycursor.fetchone()[0]

                mycursor.execute(f"SELECT COUNT(*) FROM attachments WHERE user_id = {user_id}")
                attachment_count = mycursor.fetchone()[0]

                this_user = (user_id, server_count, message_count, attachment_count)
                mycursor.execute(sqlFormulaUsers, this_user)

            else:

                mycursor.execute(f"SELECT COUNT(DISTINCT server_id) FROM messages WHERE user_id = {user_id}")
                server_count = mycursor.fetchone()[0]
                mycursor.execute(f"UPDATE users SET server_count = {server_count} WHERE user_id = {user_id}")

                mycursor.execute(f"SELECT COUNT(*) FROM messages WHERE user_id = {user_id}")
                message_count = mycursor.fetchone()[0]
                mycursor.execute(f"UPDATE users SET message_count = {message_count} WHERE user_id = {user_id}")

                mycursor.execute(f"SELECT COUNT(*) FROM attachments WHERE user_id = {user_id}")
                attachment_count = mycursor.fetchone()[0]
                mycursor.execute(f"UPDATE users SET attachment_count = {attachment_count} WHERE user_id = {user_id}")

    mydb.commit()

#Formats an inputted discord message to a list of arguments.
#Spaces in the discord message will separate the arguments.
#Quotations can be put around phrases to mitigate the space separater rule.
#For example >>command one two "three four" will return: ["one", "two", "three four"]
def getArgs(input_message_str):

    args = input_message_str.split(" ")

    if '\"' in input_message_str:
        phrase = ""
        in_quote = False
        current_index = 0
        for arg in args:

            if (in_quote == False) and (arg.startswith('\"') or arg == '\"'):
                bad_list = []
                in_quote = True

            elif (in_quote == True) and (arg.endswith('\"') or arg == '\"'):

                in_quote = False

                bad_list.append(current_index)

                if arg != " ":
                    phrase += arg + " "
                elif arg == "":
                    phrase += " "
                else:
                    phrase += arg

                for index in bad_list:
                    args[index] = "NULL"

                args[min(bad_list)] = phrase[:-1].strip('\"')
                phrase = ""

            if in_quote:

                bad_list.append(current_index)
                if arg != " ":
                    phrase += arg + " "
                elif arg == "":
                    phrase += " "
                else:
                    phrase += arg

            current_index += 1

        while "NULL" in args:
            args.remove("NULL")

    return(args)

#Enters all messages and attachments from an inputted discord guild history list into the corresponding MySQL tables messages and attachments.
def enterServerHistory(input_guild_history):

    input_guild_history = tuple(input_guild_history)

    for message in input_guild_history:

        raw_message_string = message.clean_content.replace('\n', '').replace('\\n','')

        while raw_message_string.startswith(" "):
            raw_message_string = raw_message_string[1:]

        #Timestamp--------------------------------------------------------------
        datetime = message.created_at

        #Embeds-----------------------------------------------------------------
        embed_there = False
        if len(message.embeds) != 0 and raw_message_string == "":
            embed_there = True
            embed = message.embeds[0]
            embed_dict = embed.to_dict()

            embed_to_message = ""
            if "type" in embed_dict and embed_dict["type"] == "link":
                embed_to_message += str(embed_dict["url"])
            elif "url" in embed_dict:
                embed_to_message += str(embed_dict["url"])

            else:
                if "title" in embed_dict:
                    title = str(embed_dict['title']).replace(" ","")
                    embed_to_message += f"{title} "

                if "author" in embed_dict and "name" in embed_dict["author"]:
                    name = str(embed_dict['author']['name']).replace(" ","")
                    embed_to_message += f"{name} "

                if "description" in embed_dict:
                    description = str(embed_dict['description']).replace('\r','').replace('\n','')
                    embed_to_message += f"{description} "

                if "image" in embed_dict:
                    if ("proxy_url" in embed_dict["image"]):
                        embed_to_message += f"{str(embed_dict['image']['proxy_url'])} "

                    elif "url" in embed_dict["image"]:
                        embed_to_message += f"{str(embed_dict['image']['url'])} "

        #Message----------------------------------------------------------------
        if raw_message_string != "":
            message_str = raw_message_string

            this_message = (message.id, message.author.id, message.guild.id, message.channel.id, datetime, message_str)
            mycursor.execute(sqlFormulaMessages, this_message)

        elif embed_there:
            message_str = embed_to_message

            this_message = (message.id, message.author.id, message.guild.id, message.channel.id, datetime, message_str)
            mycursor.execute(sqlFormulaMessages, this_message)

        #Attachments------------------------------------------------------------
        if len(message.attachments) > 0:
            url = message.attachments[0].url
            if url.lower().endswith(".png") or url.lower().endswith(".jpg") or url.lower().endswith(".gif"):
                attachment_str = url

                this_attachment = (message.id, message.author.id, message.guild.id, message.channel.id, datetime, attachment_str)
                mycursor.execute(sqlFormulaAttachments, this_attachment)

        mydb.commit()

#Runs when the bot comes online
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name=ACTIVITY_STATUS))
    print("Bot is running")

    if getdataloop.is_running() == False:
        getdataloop.start()

#Shutdown command---------------------------------------------------------------
@client.command()
@commands.is_owner()
async def shutdown(ctx):
    print("SHUTDOWN-------------------------------------------------------------")

    print("Bot is shutting down")
    await ctx.bot.logout()

#Ping latency command-----------------------------------------------------------
@client.command()
@commands.is_owner()
async def ping(ctx):
    print("PING-----------------------------------------------------------------")

    ping = round(client.latency * 1000)
    await ctx.send(f'Pong! {ping}ms')

#Show what servers are visible to the bot command-------------------------------
@client.command()
@commands.is_owner()
async def showservers(ctx):
    print("SHOWSERVERS--------------------------------------------------------------")

    await ctx.send("Here is a list of servers that I am in:\n")

    async for guild in client.fetch_guilds(limit=None):
        await ctx.send(f"**{guild.name}**\n*{guild.id}*\n\n")

#Add a server to the MySQL database---------------------------------------------
@client.command()
@commands.is_owner()
async def getserver(ctx):
    print("GETDATA--------------------------------------------------------------")

    args = getArgs(ctx.message.clean_content)
    guild_id = args[1]

    input_guild = client.get_guild(int(guild_id))
    print(f"Reading {input_guild.name} history...\n")

    #First use enterServerHistory() to fill out messages and attachments tables
    channel_all_history = []
    for channel in input_guild.text_channels:
        try:
            print(f"Reading #{channel} message history...")
            channel_all_history += await channel.history(limit=None).flatten()
            print(f"Finished reading #{channel} message history\n")

        except discord.Forbidden:
            print(f"\nERROR: {channel.name} could not be read.\n")

    enterServerHistory(channel_all_history)
    print("Finished reading server history.\n")

    #Now fill servers table with the inputted server, using entered data from enterServerHistory()
    mycursor.execute(f"SELECT COUNT(DISTINCT channel_id) FROM messages WHERE server_id = {guild_id}")
    channel_count = mycursor.fetchone()[0]

    users_count = len(input_guild.members)

    mycursor.execute(f"SELECT COUNT(*) FROM messages WHERE server_id = {guild_id}")
    message_count = mycursor.fetchone()[0]

    mycursor.execute(f"SELECT COUNT(*) FROM attachments WHERE server_id = {guild_id}")
    attachment_count = mycursor.fetchone()[0]

    this_server = (guild_id, channel_count, users_count, message_count, attachment_count)
    mycursor.execute(sqlFormulaServers, this_server)

    #Now fill channels table with the inputted server, using entered data from enterServerHistory()
    mycursor.execute(f"SELECT DISTINCT channel_id FROM messages WHERE server_id = {guild_id}")
    channels_list = mycursor.fetchall()

    for channel in channels_list:
        channel_id = channel[0]

        mycursor.execute(f"SELECT COUNT(*) FROM messages WHERE channel_id = {channel_id}")
        channel_message_count = mycursor.fetchone()[0]

        mycursor.execute(f"SELECT COUNT(*) FROM attachments WHERE channel_id = {channel_id}")
        channel_attachment_count = mycursor.fetchone()[0]

        this_channel = (channel_id, guild_id, channel_message_count, channel_attachment_count)
        mycursor.execute(sqlFormulaChannels, this_channel)

    #Now fill users table with the inputted server, using entered data from enterServerHistory()
    mycursor.execute("SELECT DISTINCT user_id FROM users")
    all_known_unique_users = []

    for user_id in mycursor.fetchall():
        all_known_unique_users.append(user_id[0])

    all_known_unique_users = tuple(all_known_unique_users)

    mycursor.execute(f"SELECT DISTINCT user_id FROM messages WHERE server_id = {guild_id}")
    users_with_messages_list = mycursor.fetchall()

    mycursor.execute(f"SELECT DISTINCT user_id FROM attachments WHERE server_id = {guild_id}")
    users_with_attachments_list = mycursor.fetchall()

    all_new_unique_users = tuple(np.unique(users_with_messages_list + users_with_attachments_list))

    for user_id in all_new_unique_users:

        user_id = int(user_id)

        if (user_id not in all_known_unique_users):

            server_count = 1

            mycursor.execute(f"SELECT COUNT(*) FROM messages WHERE user_id = {user_id}")
            message_count = mycursor.fetchone()[0]

            mycursor.execute(f"SELECT COUNT(*) FROM attachments WHERE user_id = {user_id}")
            attachment_count = mycursor.fetchone()[0]

            this_user = (user_id, server_count, message_count, attachment_count)
            mycursor.execute(sqlFormulaUsers, this_user)

        else:

            mycursor.execute(f"UPDATE users SET server_count = server_count + 1 WHERE user_id = {user_id}")

            mycursor.execute(f"SELECT COUNT(*) FROM messages WHERE user_id = {user_id}")
            message_count = mycursor.fetchone()[0]
            mycursor.execute(f"UPDATE users SET message_count = {message_count} WHERE user_id = {user_id}")

            mycursor.execute(f"SELECT COUNT(*) FROM attachments WHERE user_id = {user_id}")
            attachment_count = mycursor.fetchone()[0]
            mycursor.execute(f"UPDATE users SET attachment_count = {attachment_count} WHERE user_id = {user_id}")

    mydb.commit()

client.run(TOKEN)
