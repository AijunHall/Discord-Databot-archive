import math
import random as rdm
import time
import pytz
import datetime
import os
import shutil
import csv
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager
from matplotlib.ticker import MaxNLocator
import discord
from discord.ext import commands
from discord.utils import get

timezone_dict = {

    "eastern":"US/Eastern",
    "pacific":"US/Pacific",
    "central":"US/Central"
}

TOKEN = ""
COMMAND_PREFIX = ">>"
ACTIVITY_STATUS = f"{COMMAND_PREFIX}help"
TIMEZONE = timezone_dict["eastern"]
WORKING_DIRECTORY = os.getcwd()

tz = pytz.timezone(TIMEZONE)
old_tz = pytz.timezone("UTC")

client = commands.Bot(command_prefix = COMMAND_PREFIX)
client.remove_command("help")

def getargs(input_message_str):

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

def navigatedir(input_server_id,input_channel_id=0):

    path_found = False

    if input_channel_id == 0:

        for file in os.listdir("./"):
            if file.startswith(str(input_server_id)):
                os.chdir(file)
                path_found = True
                break

    else:

        for file in os.listdir("./"):
            if file.startswith(str(input_server_id)):
                os.chdir(file)

                for file in os.listdir("./"):
                    if file.startswith(str(input_channel_id)):
                        os.chdir(file)
                        path_found = True
                        break
                break

    if path_found == True:
        print(f"Moved working directory to:\n{os.getcwd()}")
    else:
        print("ERROR: Unable to move to specified directory")

def checkServer(input_server):

    servers_txtfile = open(r"servers.txt","r",encoding='utf-8')
    raw_data = servers_txtfile.readlines()

    def strip(string):
        return string.strip('\n')

    raw_data = list(map(strip, raw_data))
    servers_txtfile.close()

    server_id = input_server.id
    server_name = input_server.name.strip(">")

    server_text_channels = ""
    for channel in input_server.text_channels:
        server_text_channels += f"{channel.id}-{channel.name},"

    server_id_tag = f"<SERVER_ID:{server_id}>"
    server_name_tag = f"<SERVER_NAME:{server_name}>"
    channels_tag = f"<TEXT_CHANNELS:{server_text_channels[:-1]}>"

    server_info = f"{server_id_tag} {server_name_tag} {channels_tag}"

    server_there = False

    for line in raw_data:
        guild_fields = line.split(">")

        if str(input_server.id) in guild_fields[0]:
            server_there = True

    if server_there:
        return False
    else:
        return server_info

def getServer(input_server):

    servers_txtfile = open(r"servers.txt","r",encoding='utf-8')
    raw_data = servers_txtfile.readlines()

    def strip(string):
        return string.strip('\n')

    raw_data = list(map(strip, raw_data))
    servers_txtfile.close()

    result = ""
    for server_info in raw_data:
        if str(input_server.id) in server_info:
            result = server_info
            break

    if result == "":
        print("ERROR: getServer was not able to find server_info")
        return
    else:
        return result

def rewriteServer(input_server):

    servers_txtfile = open(r"servers.txt","r+",encoding='utf-8')
    raw_data = servers_txtfile.readlines()

    def strip(string):
        return string.strip('\n')

    raw_data = list(map(strip, raw_data))
    servers_txtfile.close()

    server_id = input_server.id
    server_name = input_server.name.strip(">")

    server_text_channels = ""
    for channel in input_server.text_channels:
        server_text_channels += f"{channel.id}-{channel.name},"

    server_id_tag = f"<SERVER_ID:{server_id}>"
    server_name_tag = f"<SERVER_NAME:{server_name}>"
    channels_tag = f"<TEXT_CHANNELS:{server_text_channels[:-1]}>"

    server_info = f"{server_id_tag} {server_name_tag} {channels_tag}"

    for i in range(len(raw_data)):
        guild_fields = raw_data[i].split(">")
        if str(input_server.id) in guild_fields[0]:
            raw_data.pop(i)
            break
    raw_data.append(server_info)

    servers_txtfile = open(r"servers.txt","w+",encoding='utf-8')

    for line in raw_data:
        servers_txtfile.write(f"{line}\n")

    servers_txtfile.close()

def getChannelID(input_channel_name,input_channel_fields):

    channel_fields = input_channel_fields[16:].split(",")

    for channel_info in channel_fields:

        channel_name = channel_info.split("-",1)[1]

        if input_channel_name == channel_name:

            return channel_info[:18]

    print("ERROR: Unable to get channel ID from specified channel name")

def getChannelName(input_channel_id,input_channel_fields):

    channel_fields = input_channel_fields[16:].split(",")

    for channel_info in channel_fields:

        channel_id = channel_info.split("-",1)[0]

        if str(input_channel_id) == channel_id:

            return channel_info[19:]

    print("ERROR: Unable to get channel Name from specified channel id")

def removeChannel(input_server_id, input_channel_id):

    servers_txtfile = open(r"servers.txt","r+",encoding='utf-8')
    raw_data = servers_txtfile.readlines()

    def strip(string):
        return string.strip('\n')

    raw_data = list(map(strip, raw_data))
    servers_txtfile.close()

    for i in range(len(raw_data)):

        guild_fields = raw_data[i].split(">")

        if str(input_server_id) in guild_fields[0]:

            channel_fields = guild_fields[2][16:].split(",")

            for j in range(len(channel_fields)):
                if str(input_channel_id) in channel_fields[j]:
                    channel_fields.pop(j)
                    break

            new_channel_fields = "<TEXT_CHANNELS:"
            for channel_info in channel_fields:
                new_channel_fields += channel_info + ","

            new_guild_field = f"{guild_fields[0]}>{guild_fields[1]}> {new_channel_fields[:-1]}>"
            raw_data[i] = new_guild_field
            break

    servers_txtfile = open(r"servers.txt","w+",encoding='utf-8')

    for line in raw_data:
        servers_txtfile.write(f"{line}\n")

    servers_txtfile.close()

    navigatedir(input_server_id)

    for file in os.listdir("./"):
        if file.startswith(str(input_channel_id)):
            shutil.rmtree(file)
            break

    os.chdir(WORKING_DIRECTORY)

    print("Channel successfully deleted")

def deleteServer(input_server):

    servers_txtfile = open(r"servers.txt","r",encoding='utf-8')
    raw_data = servers_txtfile.readlines()

    def strip(string):
        return string.strip('\n')

    raw_data = list(map(strip, raw_data))
    servers_txtfile.close()

    for i in range(len(raw_data)):
        guild_fields = raw_data[i].split(">")
        if str(input_server.id) in guild_fields[0]:
            raw_data.pop(i)
            break

    servers_txtfile = open(r"servers.txt","w+",encoding='utf-8')

    for line in raw_data:
        servers_txtfile.write(f"{line}\n")

    servers_txtfile.close()

def striptoMessages(input_df):
    print(f"Creating a stripped messages dataframe")

    all_user_messages = []
    for username in input_df.columns:

        username_df = input_df[username]
        tags = username_df.str.split(" ",2)

        timestamp_raw = tags.str[0]
        timestamp_raw = timestamp_raw = timestamp_raw.str[11:-1]

        message_raw = tags.str[2]
        message_raw = message_raw.str[9:-1]
        message_raw = message_raw[message_raw.str.match("NULL") == False]

        read_line = timestamp_raw + " " + message_raw
        all_user_messages.append(read_line)

    max_row_num = 0
    for username in input_df.columns:
        this_row_length = int(len(input_df[username]))
        if this_row_length > max_row_num:
            max_row_num = this_row_length

    dead_list = []
    for i in range(max_row_num):
        dead_list.append(" ")

    input_df_messages = pd.DataFrame()
    input_df_messages["dud"] = dead_list

    i = 0
    for username in input_df.columns:
        input_df_messages[username] = all_user_messages[i]
        i += 1

    input_df_messages.drop(["dud"], axis=1, inplace=True)

    return input_df_messages

def striptoAttachments(input_df):
    print(f"Creating a stripped attachments dataframe")

    all_user_attachments = []
    for username in input_df.columns:

        username_df = input_df[username]
        tags = username_df.str.split(" ",2)

        timestamp_raw = tags.str[0]
        timestamp_raw = timestamp_raw.str[11:-1]

        attachment_raw = tags.str[1]
        attachment_raw = attachment_raw.str[12:-1]

        read_line = timestamp_raw + " " + attachment_raw
        all_user_attachments.append(read_line)

    max_row_num = 0
    for username in input_df.columns:
        this_row_length = int(len(input_df[username]))
        if this_row_length > max_row_num:
            max_row_num = this_row_length

    dead_list = []
    for i in range(max_row_num):
        dead_list.append(" ")

    input_df_attachments = pd.DataFrame()
    input_df_attachments["dud"] = dead_list

    i = 0
    for username in input_df.columns:
        input_df_attachments[username] = all_user_attachments[i]
        i += 1

    input_df_attachments.drop(["dud"], axis=1, inplace=True)

    return input_df_attachments

def striptoDaily(input_df):
    print("Creating a stripped daily dataframe")

    all_days = []
    for username in input_df.columns:
        username_df = input_df[username].dropna()
        username_unique_days = (username_df.str[:10].str.replace("-","")).unique()
        for day in username_unique_days:
            day_int = int(day)
            if day_int not in all_days:
                all_days.append(day_int)

    all_days.sort(reverse=True)

    def stringafy(input_day_int):
        day_str = str(input_day_int)
        return day_str[:4] + "-" + day_str[4:6] + "-" + day_str[6:]

    all_days = list(map(stringafy,all_days))

    daily_df = pd.DataFrame([], index=all_days, columns=input_df.columns)

    for username in input_df.columns:
        username_column = []
        username_df = input_df[username].dropna()
        for day in all_days:
            username_day_tuple = tuple(username_df[username_df.str.startswith(day)].tolist())
            if len(username_day_tuple) != 0:
                csv_cell_str = ""
                for message in username_day_tuple:
                    csv_cell_str += message + '\n'

                username_column.append(csv_cell_str)
            else:
                username_column.append(np.nan)

        daily_df[username] = username_column

    return daily_df

def channelwritetxt(input_filename,input_channelHistory):
    print(f"Creating {input_filename}.txt")

    readto_txtfile = open(f"{input_filename}.txt","w+",encoding='utf-8')

    all_messages = tuple(input_channelHistory)
    line_count = len(all_messages)

    for message in all_messages:

        raw_message_string = message.clean_content.replace('\n', '').replace('\\n','')

        while raw_message_string.startswith(" "):
            raw_message_string = raw_message_string[1:]

        timestamp = old_tz.localize(message.created_at).astimezone(tz)
        timestamp_str = str(timestamp)[:19]
        date_str = timestamp_str[:10]
        time_str = timestamp_str[11:16]

        #Timestamp--------------------------------------------------------------
        if int(time_str[:2]) > 12:
            time_str = str(int(time_str[:2]) - 12) + time_str[2:] + "PM"
        else:
            time_str += "AM"

        if time_str[:2].endswith(":"):
            time_str = "0" + time_str

        timestamp_str = f"<TIMESTAMP:{date_str}|{time_str}>"

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

        #Attachments------------------------------------------------------------
        if len(message.attachments) > 0:
            url = message.attachments[0].url
            if url.lower().endswith(".png") or url.lower().endswith(".jpg") or url.lower().endswith(".gif"):
                attachment_str = f"<ATTACHMENT:{url}>"
        else:
            attachment_str = f"<ATTACHMENT:NULL>"

        #Author-----------------------------------------------------------------
        author = str(message.author.display_name).replace(" ","")
        author_str = f"<AUTHOR:{author}>"

        #Message----------------------------------------------------------------
        if raw_message_string != "":
            message_str = f"<MESSAGE:{raw_message_string}>"

        elif embed_there:
            message_str = f"<MESSAGE:{embed_to_message}>"

        else:
            message_str = f"<MESSAGE:NULL>"


        readto_txtfile.write(f"{timestamp_str} {author_str} {attachment_str} {message_str}\n")

    print(f"{input_filename}.txt has been created from {line_count} lines\n")
    readto_txtfile.close()

def channelwritecsv(input_txtfile):
    print(f"Creating {input_txtfile}.csv files")

    readto_txtfile = open(f"{input_txtfile}.txt","r",encoding='utf-8')
    raw_data = readto_txtfile.readlines()

    with open(f"{input_txtfile}.csv", "w+", newline="", encoding='utf-8') as f:

        writer = csv.writer(f)

        if len(raw_data) == 0:
            print(f"{input_txtfile} is empty. Created empty csv file")
            readto_txtfile.close()
            f.close()
            return

        all_usernames = []
        all_messages = []

        for line in raw_data:

            line = line.split(" ",3)
            timestamp_tag = line[0]
            author_tag = line[1]
            attachment_tag = line[2]
            message_tag = line[3].strip('\n')
            username = author_tag[8:-1]

            all_messages.append(f"{username} {timestamp_tag} {attachment_tag} {message_tag}")

            if username not in all_usernames:
                all_usernames.append(username)

        writer.writerow(all_usernames)

        #2D list which contains lists that contain all messages of a specific username.
        #User's index in all_usernames corresponds to their column index
        #For example: user1, user2, user3 ----> 0, 1, 2,
        all_user_messages = []

        for username in all_usernames:
            all_user_messages.append([])

        for message in all_messages:
            for username in all_usernames:
                username_length = len(username)
                if message[:username_length] == username and message[username_length] == " ":
                    index = all_usernames.index(username)
                    message_string = message[len(username)+1:]
                    all_user_messages[index].append(message_string)

        #Find username with the most messages and store that value in max_amount.
        #The csv writer needs to be passed a row of equal size to the amount of usernames.
        #Therefore we make all username message lists in all_user_messages have equal length (by adding null values)
        max_amount = 0

        for message_list in all_user_messages:
            if len(message_list) > max_amount:
                max_amount = len(message_list)

        for message_list in all_user_messages:
            while len(message_list) != max_amount:
                message_list.append("")

        #Iterate through all the lists in all_user_messages, and add each users message to thiswriterow[].
        #thiswriterow[] is what will be written to the csv file per row.
        j = 0
        for i in range(max_amount):
            thiswriterow = []
            all_user_messages_length = range(len(all_user_messages))

            for message_list in all_user_messages_length:
                message_string = all_user_messages[message_list][j]
                thiswriterow.append(message_string)

            writer.writerow(thiswriterow)
            j += 1

    discord_df = pd.read_csv(f"{input_txtfile}.csv", dtype="str")

    stripped_messages_df = striptoMessages(discord_df)
    stripped_attachments_df = striptoAttachments(discord_df)
    stripped_messages_daily_df = striptoDaily(stripped_messages_df)
    stripped_attachments_daily_df = striptoDaily(stripped_attachments_df)

    stripped_messages_df.to_csv(f"{input_txtfile} strippedMessages.csv",index=False)
    stripped_attachments_df.to_csv(f"{input_txtfile} strippedAttachments.csv",index=False)
    stripped_messages_daily_df.to_csv(f"{input_txtfile} strippedMessagesDaily.csv",index=True)
    stripped_attachments_daily_df.to_csv(f"{input_txtfile} strippedAttachmentsDaily.csv",index=True)

    print(f"{input_txtfile}.csv files have been created\n")
    readto_txtfile.close()
    f.close()

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name=ACTIVITY_STATUS))
    print("Bot is running")
    print(f"The default working directory is:\n{WORKING_DIRECTORY}")

#Help command-------------------------------------------------------------------
@client.command()
async def help(ctx):
    print("HELP-----------------------------------------------------------------")

    help_txtfile = open(r"help.txt","r",encoding='utf-8')
    raw_data = tuple(help_txtfile.readlines())
    output_str = ""

    for line in raw_data:
        output_str += line

    await ctx.send(output_str)

    help_txtfile.close()

#Shutdown command---------------------------------------------------------------
@client.command()
@commands.is_owner()
async def shutdown(ctx):
    print("SHUTDOWN-------------------------------------------------------------")

    print("Bot is shutting down")
    await ctx.bot.logout()

#Ping latency command-----------------------------------------------------------
@client.command()
async def ping(ctx):
    print("PING-----------------------------------------------------------------")

    ping = round(client.latency * 1000)
    await ctx.send(f'Pong! {ping}ms')

#Adding a server to the database command----------------------------------------
@client.command()
@commands.is_owner()
async def getdata(ctx):
    print("GETDATA--------------------------------------------------------------")

    server_info = checkServer(ctx.guild)

    if server_info == False:
        print(f"{ctx.guild.name} already in the database\n")
    else:
        print(f"New server found: {ctx.guild.name}")

        servers_txtfile = open(r"servers.txt","a",encoding='utf-8')
        servers_txtfile.write(f"{server_info}\n")
        servers_txtfile.close()

        server_folder_name = f"{ctx.guild.id} - ({ctx.guild.name})"
        os.mkdir(server_folder_name)
        os.chdir(server_folder_name)

        total_channelHistory = []

        for channel in ctx.guild.text_channels:

            try:
                channel_tag = f"{channel.id} - (#{channel.name})"

                os.mkdir(channel_tag)
                os.chdir(channel_tag)

                print(f"Reading #{channel} channel history...")
                channelHistory = await channel.history(limit=None).flatten()
                print(f"Finished reading #{channel} channel history\n")

                total_channelHistory += channelHistory

                channelwritetxt(channel.id,channelHistory)
                channelwritecsv(channel.id)

                os.chdir("../")
            except discord.Forbidden:
                print(f"\nERROR: {channel.name} could not be read. Preparing to erase channel...\n")
                os.chdir(WORKING_DIRECTORY)
                removeChannel(ctx.guild.id, channel.id)
                os.chdir(server_folder_name)

        channelwritetxt(ctx.guild.id,total_channelHistory)
        channelwritecsv(ctx.guild.id)

        print("All channels read through successfully\n")
        print("Server database successfuly created")

        os.chdir(WORKING_DIRECTORY)
        print(f"Current working directory:\n{os.getcwd()}")

#Updating a server or channel to the database command---------------------------
@client.command()
@commands.is_owner()
async def updatedata(ctx):
    print("UPDATEDATA-----------------------------------------------------------")

    serverthere = checkServer(ctx.guild)

    if serverthere != False:
        print("ERROR: Server database does not exist")
        os.chdir(WORKING_DIRECTORY)
        return

    args = getargs(ctx.message.clean_content)

    guild_info = getServer(ctx.guild)
    guild_fields = guild_info.split(">")
    channel_fields = guild_fields[2]

    cond1 = (len(args) == 2 and args[1].lower() == "server")
    cond2 = (len(args) == 3 and args[1].lower() == "channel" and args[2] in channel_fields)
    arg_validation = (cond1 or cond2)

    if arg_validation == False:
        print("ERROR: Invalid args")
        os.chdir(WORKING_DIRECTORY)
        return

    if cond1:

        rewriteServer(ctx.guild)

        for file in os.listdir("./"):
            if file.startswith(str(ctx.guild.id)):
                shutil.rmtree(file)
                break

        server_folder_name = f"{ctx.guild.id} - ({ctx.guild.name})"
        os.mkdir(server_folder_name)
        os.chdir(server_folder_name)

        total_channelHistory = []

        for channel in ctx.guild.text_channels:
            try:
                channel_tag = f"{channel.id} - (#{channel.name})"

                os.mkdir(channel_tag)
                os.chdir(channel_tag)

                print(f"Reading #{channel} channel history...")
                channelHistory = await channel.history(limit=None).flatten()
                print(f"Finished reading #{channel} channel history\n")

                total_channelHistory += channelHistory

                channelwritetxt(channel.id,channelHistory)
                channelwritecsv(channel.id)

                os.chdir("../")
            except discord.Forbidden:
                print(f"\nERROR: {channel.name} could not be read. Preparing to erase channel...\n")
                os.chdir(WORKING_DIRECTORY)
                removeChannel(ctx.guild.id, channel.id)
                os.chdir(server_folder_name)

        channelwritetxt(ctx.guild.id,total_channelHistory)
        channelwritecsv(ctx.guild.id)

        print("All channels read through successfully\n")

    elif cond2:

        input = args[2]

        channels = ctx.guild.text_channels
        channel_id = ""
        channel_history = []

        try:
            for channel in channels:
                if input == channel.name:
                    channel_id = channel.id
                    print(f"Reading #{channel} channel history...")
                    channelHistory = await channel.history(limit=None).flatten()
                    print(f"Finished reading #{channel} channel history")
                    break

            for file in os.listdir("./"):
                if file.startswith(str(ctx.guild.id)):
                    os.chdir(file)

                    for file in os.listdir("./"):
                        if input in file:
                            os.chdir(file)

                            for file in os.listdir("./"):
                                os.remove(file)

                            channelwritetxt(channel_id,channelHistory)
                            channelwritecsv(channel_id)

                            break
                    break

            print("Server database successfuly updated")
        except discord.Forbidden:
            print(f"\nERROR: {channel.name} could not be read. Preparing to erase channel...\n")
            os.chdir(WORKING_DIRECTORY)
            removeChannel(ctx.guild.id, channel.id)

    os.chdir(WORKING_DIRECTORY)
    print(f"Current working directory:\n{os.getcwd()}")

#Deleting a server from the database command------------------------------------
@client.command()
@commands.is_owner()
async def deletedata(ctx):
    print("DELETEDATA-----------------------------------------------------------")

    serverthere = checkServer(ctx.guild)

    if serverthere != False:
        print("ERROR: Server database does not exist")
        return

    deleteServer(ctx.guild)

    for file in os.listdir("./"):
        if file.startswith(str(ctx.guild.id)):
            shutil.rmtree(file)
            break

    print("Server database successfully deleted")

#allmsgs command----------------------------------------------------------------
@client.command()
async def allmsgs(ctx):
    print("ALLMSGS--------------------------------------------------------------")

    serverthere = checkServer(ctx.guild)

    if serverthere != False:
        print("ERROR: Server database does not exist")
        os.chdir(WORKING_DIRECTORY)
        return

    args = getargs(ctx.message.clean_content)

    guild_info = getServer(ctx.guild)
    guild_fields = guild_info.split(">")
    channel_fields = guild_fields[2]

    if len(args) >= 2 and args[1] in channel_fields:

        channel_id = getChannelID(args[1], channel_fields)

        navigatedir(ctx.guild.id,channel_id)

        data = pd.read_csv(f"{channel_id} strippedMessages.csv", dtype="str")

    else:

        navigatedir(ctx.guild.id)

        data = pd.read_csv(f"{ctx.guild.id} strippedMessages.csv", dtype="str")

    cond1 = (len(args) == 1)
    cond2 = (len(args) == 2 and args[1] in data.columns)
    cond3 = (len(args) == 2 and args[1].lower() == "bar")
    cond4 = (len(args) == 2 and args[1].lower() == "pie")

    cond5 = (len(args) == 2 and args[1] in channel_fields)
    cond6 = (len(args) == 3 and args[1] in channel_fields and args[2] in data.columns)
    cond7 = (len(args) == 3 and args[1] in channel_fields and args[2].lower() == "bar")
    cond8 = (len(args) == 3 and args[1] in channel_fields and args[2].lower() == "pie")

    arg_validation = (cond1 or cond2 or cond3 or cond4 or cond5 or cond6 or cond7 or cond8)

    if arg_validation == False:
        print("ERROR: Invalid args")
        os.chdir(WORKING_DIRECTORY)
        return

    data_count = data.count()

    total_messages = 0
    for username in data_count.index:
        total_messages += data_count[username]

    MIN_MESSAGE_AMOUNT = math.floor(total_messages * 0.01)
    FONT_SIZE = 30

    if cond1:
        print("Sending allmsgs plaintext")

        data = data.count().sort_values()[::-1]
        data = data[data > MIN_MESSAGE_AMOUNT/2].dropna()

        output_str = ""

        for username in data.index:
            username_count = data[username]
            output_str += f"**{username}** has typed **{username_count}** messages throughout the entire server!\n"

        output_str += f"\nIn total there were **{total_messages}** messages typed throughout the entire server!"
        await ctx.send(output_str)

    elif cond2:
        print("Sending allmsgs username plaintext")

        username = args[1]

        data = data.count()

        output_str = f"**{username}** has typed **{data[username]}** messages throughout the entire server!"
        await ctx.send(output_str)

    elif cond3:
        print("Creating bar graph...")

        data = data.count().sort_values()
        data = data[data > MIN_MESSAGE_AMOUNT].dropna()

        graph_axes = data.plot(kind="barh", edgecolor="black", linewidth="3")
        graph_fig = plt.gcf()

        graph_axes.tick_params(labelsize=int(FONT_SIZE/1.5))
        graph_axes.set_title(f"All collected user's messages from {ctx.guild.name}", fontname="Arial", fontsize=int(FONT_SIZE*2))
        graph_axes.set_ylabel("Users", fontname="Arial", fontsize=int(FONT_SIZE*1.5))
        graph_axes.set_xlabel("Number of messages typed", fontname="Arial", fontsize=int(FONT_SIZE*1.5))
        graph_fig.set_size_inches(30,15)

        print("Saving graph...")
        graph_fig.savefig("allmsgs_bar.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        allmsgs_bar_png = open("allmsgs_bar.png", "rb")
        discord_allmsgs_bar_png = discord.File(fp=allmsgs_bar_png,filename="allmsgs_bar.png")
        await ctx.send(file=discord_allmsgs_bar_png)

        allmsgs_bar_png.close()

    elif cond4:
        print("Creating pie graph...")

        data = data.count().sort_values()[::-1]
        data = data[data > MIN_MESSAGE_AMOUNT].dropna()

        graph_axes = data.plot(kind="pie", labels=None)
        graph_fig = plt.gcf()

        graph_axes.pie(data, autopct='%1.1f%%', labels=data.index, textprops={'fontsize': FONT_SIZE}, wedgeprops={'linewidth': 3, 'edgecolor': "black"})
        legend = graph_axes.legend(loc=2, prop={'size': FONT_SIZE*1.5})
        graph_fig.set_size_inches(30,30)
        graph_axes.set_ylabel("")
        graph_axes.set_title(f"User percentage of all messages in {ctx.guild.name}", {'fontsize': FONT_SIZE*3}, fontname="Arial")

        # Change to location of the legend.
        bb = legend.get_bbox_to_anchor().inverse_transformed(graph_axes.transAxes)
        xOffset = 1.25
        bb.x0 = xOffset
        bb.x1 = xOffset
        legend.set_bbox_to_anchor(bb, transform = graph_axes.transAxes)

        print("Saving graph...")
        graph_fig.savefig("allmsgs_pie.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        allmsgs_pie_png = open("allmsgs_pie.png", "rb")
        discord_allmsgs_pie_png = discord.File(fp=allmsgs_pie_png,filename="allmsgs_pie.png")
        await ctx.send(file=discord_allmsgs_pie_png)

        allmsgs_pie_png.close()

    elif cond5:
        print("Sending allmsgs plaintext")

        data = data.count().sort_values()[::-1]
        data = data[data > MIN_MESSAGE_AMOUNT/2].dropna()

        output_str = ""

        for username in data.index:
            username_count = data[username]
            output_str += f"**{username}** has typed **{username_count}** messages in the #{args[1]} channel!\n"

        output_str += f"\nIn total there were **{total_messages}** messages typed in the #{args[1]} channel!"
        await ctx.send(output_str)

    elif cond6:
        print("Sending allmsgs username plaintext")

        username = args[2]

        data = data.count()

        output_str = f"**{username}** has typed **{data[username]}** messages in the #{args[1]} channel!"
        await ctx.send(output_str)

    elif cond7:
        print("Creating bar graph...")

        data = data.count().sort_values()
        data = data[data > MIN_MESSAGE_AMOUNT].dropna()

        graph_axes = data.plot(kind="barh", edgecolor="black", linewidth="3")
        graph_fig = plt.gcf()

        graph_axes.tick_params(labelsize=int(FONT_SIZE/1.5))
        graph_axes.set_title(f"All collected user's messages from #{args[1]}", fontname="Arial", fontsize=int(FONT_SIZE*2))
        graph_axes.set_ylabel("Users", fontname="Arial", fontsize=int(FONT_SIZE*1.5))
        graph_axes.set_xlabel("Number of messages typed", fontname="Arial", fontsize=int(FONT_SIZE*1.5))
        graph_fig.set_size_inches(30,15)

        print("Saving graph...")
        graph_fig.savefig("allmsgs_bar.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        allmsgs_bar_png = open("allmsgs_bar.png", "rb")
        discord_allmsgs_bar_png = discord.File(fp=allmsgs_bar_png,filename="allmsgs_bar.png")
        await ctx.send(file=discord_allmsgs_bar_png)

        allmsgs_bar_png.close()

    elif cond8:
        print("Creating pie graph...")

        data = data.count().sort_values()[::-1]
        data = data[data > MIN_MESSAGE_AMOUNT].dropna()

        graph_axes = data.plot(kind="pie", labels=None)
        graph_fig = plt.gcf()

        graph_axes.pie(data, autopct='%1.1f%%', labels=data.index, textprops={'fontsize': FONT_SIZE}, wedgeprops={'linewidth': 3, 'edgecolor': "black"})
        legend = graph_axes.legend(loc=2, prop={'size': FONT_SIZE*1.5})
        graph_fig.set_size_inches(30,30)
        graph_axes.set_ylabel("")
        graph_axes.set_title(f"User percentage of all messages in #{args[1]}", {'fontsize': FONT_SIZE*3}, fontname="Arial")

        # Change to location of the legend.
        bb = legend.get_bbox_to_anchor().inverse_transformed(graph_axes.transAxes)
        xOffset = 1.25
        bb.x0 = xOffset
        bb.x1 = xOffset
        legend.set_bbox_to_anchor(bb, transform = graph_axes.transAxes)

        print("Saving graph...")
        graph_fig.savefig("allmsgs_pie.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        allmsgs_pie_png = open("allmsgs_pie.png", "rb")
        discord_allmsgs_pie_png = discord.File(fp=allmsgs_pie_png,filename="allmsgs_pie.png")
        await ctx.send(file=discord_allmsgs_pie_png)

        allmsgs_pie_png.close()

    os.chdir(WORKING_DIRECTORY)

    print(f"Current working directory:\n{os.getcwd()}")

#allattachments command---------------------------------------------------------
@client.command()
async def allattachments(ctx):
    print("ALLATTACHMENTS-------------------------------------------------------")

    serverthere = checkServer(ctx.guild)

    if serverthere != False:
        print("ERROR: Server database does not exist")
        os.chdir(WORKING_DIRECTORY)
        return

    args = getargs(ctx.message.clean_content)

    guild_info = getServer(ctx.guild)
    guild_fields = guild_info.split(">")
    channel_fields = guild_fields[2]

    if len(args) >= 2 and args[1] in channel_fields:

        channel_id = getChannelID(args[1], channel_fields)

        navigatedir(ctx.guild.id,channel_id)

        data = pd.read_csv(f"{channel_id} strippedAttachments.csv", dtype="str")

    else:

        navigatedir(ctx.guild.id)

        data = pd.read_csv(f"{ctx.guild.id} strippedAttachments.csv", dtype="str")

    cond1 = (len(args) == 1)
    cond2 = (len(args) == 2 and args[1] in data.columns)
    cond3 = (len(args) == 2 and args[1].lower() == "bar")
    cond4 = (len(args) == 2 and args[1].lower() == "pie")

    cond5 = (len(args) == 2 and args[1] in channel_fields)
    cond6 = (len(args) == 3 and args[1] in channel_fields and args[2] in data.columns)
    cond7 = (len(args) == 3 and args[1] in channel_fields and args[2].lower() == "bar")
    cond8 = (len(args) == 3 and args[1] in channel_fields and args[2].lower() == "pie")

    arg_validation = (cond1 or cond2 or cond3 or cond4 or cond5 or cond6 or cond7 or cond8)

    if arg_validation == False:
        print("ERROR: Invalid args")
        os.chdir(WORKING_DIRECTORY)
        return

    for username in data.columns:
        data[username] = data[username][data[username].str.endswith("NULL") == False]

    data_count = data.count()

    total_attachments = 0
    for username in data_count.index:
        total_attachments += data_count[username]

    MIN_MESSAGE_AMOUNT = math.floor(total_attachments * 0.01)
    FONT_SIZE = 30

    if cond1:
        print("Sending allattachments plaintext")

        data = data.count().sort_values()[::-1]
        data = data[data > MIN_MESSAGE_AMOUNT/2].dropna()

        output_str = ""

        for username in data.index:
            username_count = data[username]
            output_str += f"**{username}** has sent **{username_count}** attachments throughout the entire server!\n"

        output_str += f"\nIn total there were **{total_attachments}** attachments sent throughout the entire server!"
        await ctx.send(output_str)

    elif cond2:
        print("Sending allattachments username plaintext")

        username = args[1]

        data = data.count()

        output_str = f"**{username}** has sent **{data[username]}** attachments throughout the entire server!"
        await ctx.send(output_str)

    elif cond3:
        print("Creating bar graph...")

        data = data.count().sort_values()
        data = data[data > MIN_MESSAGE_AMOUNT].dropna()

        graph_axes = data.plot(kind="barh", edgecolor="black", linewidth="3")
        graph_fig = plt.gcf()

        graph_axes.tick_params(labelsize=int(FONT_SIZE/1.5))
        graph_axes.set_title(f"All collected user's attachments in {ctx.guild.name}", fontname="Arial", fontsize=int(FONT_SIZE*2))
        graph_axes.set_ylabel("Users", fontname="Arial", fontsize=int(FONT_SIZE*1.5))
        graph_axes.set_xlabel("Number of attachments sent", fontname="Arial", fontsize=int(FONT_SIZE*1.5))
        graph_fig.set_size_inches(30,15)

        print("Saving graph...")
        graph_fig.savefig("allattachments_bar.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        allattachments_bar_png = open("allattachments_bar.png", "rb")
        discord_allattachments_bar_png = discord.File(fp=allattachments_bar_png,filename="allattachments_bar.png")
        await ctx.send(file=discord_allattachments_bar_png)

        allattachments_bar_png.close()

    elif cond4:
        print("Creating pie graph...")

        data = data.count().sort_values()[::-1]
        data = data[data > MIN_MESSAGE_AMOUNT].dropna()

        graph_axes = data.plot(kind="pie", labels=None)
        graph_fig = plt.gcf()

        graph_axes.pie(data, autopct='%1.1f%%', labels=data.index, textprops={'fontsize': FONT_SIZE}, wedgeprops={'linewidth': 3, 'edgecolor': "black"})
        legend = graph_axes.legend(loc=2, prop={'size': FONT_SIZE*1.5})
        graph_fig.set_size_inches(30,30)
        graph_axes.set_ylabel("")
        graph_axes.set_title(f"User percentage of all attachments in {ctx.guild.name}", {'fontsize': FONT_SIZE*3}, fontname="Arial")

        # Change to location of the legend.
        bb = legend.get_bbox_to_anchor().inverse_transformed(graph_axes.transAxes)
        xOffset = 1.25
        bb.x0 = xOffset
        bb.x1 = xOffset
        legend.set_bbox_to_anchor(bb, transform = graph_axes.transAxes)

        print("Saving graph...")
        graph_fig.savefig("allattachments_pie.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        allattachments_pie_png = open("allattachments_pie.png", "rb")
        discord_allattachments_pie_png = discord.File(fp=allattachments_pie_png,filename="allattachments_pie.png")
        await ctx.send(file=discord_allattachments_pie_png)

        allattachments_pie_png.close()

    elif cond5:
        print("Sending allattachments plaintext")

        data = data.count().sort_values()[::-1]
        data = data[data > MIN_MESSAGE_AMOUNT/2].dropna()

        output_str = ""

        for username in data.index:
            username_count = data[username]
            output_str += f"**{username}** has sent **{username_count}** attachments in the #{args[1]} channel!\n"

        output_str += f"\nIn total there were **{total_attachments}** attachments sent in the #{args[1]} channel!"
        await ctx.send(output_str)

    elif cond6:
        print("Sending allattachments username plaintext")

        username = args[2]

        data = data.count()

        output_str = f"**{username}** has sent **{data[username]}** attachments in the #{args[1]} channel!"
        await ctx.send(output_str)

    elif cond7:
        print("Creating bar graph...")

        data = data.count().sort_values()
        data = data[data > MIN_MESSAGE_AMOUNT].dropna()

        graph_axes = data.plot(kind="barh", edgecolor="black", linewidth="3")
        graph_fig = plt.gcf()

        graph_axes.tick_params(labelsize=int(FONT_SIZE/1.5))
        graph_axes.set_title(f"All collected user's attachments from #{args[1]}", fontname="Arial", fontsize=int(FONT_SIZE*2))
        graph_axes.set_ylabel("Users", fontname="Arial", fontsize=int(FONT_SIZE*1.5))
        graph_axes.set_xlabel("Number of attachments sent", fontname="Arial", fontsize=int(FONT_SIZE*1.5))
        graph_fig.set_size_inches(30,15)

        print("Saving graph...")
        graph_fig.savefig("allattachments_bar.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        allattachments_bar_png = open("allattachments_bar.png", "rb")
        discord_allattachments_bar_png = discord.File(fp=allattachments_bar_png,filename="allattachments_bar.png")
        await ctx.send(file=discord_allattachments_bar_png)

        allattachments_bar_png.close()

    elif cond8:
        print("Creating pie graph...")

        data = data.count().sort_values()[::-1]
        data = data[data > MIN_MESSAGE_AMOUNT].dropna()

        graph_axes = data.plot(kind="pie", labels=None)
        graph_fig = plt.gcf()

        graph_axes.pie(data, autopct='%1.1f%%', labels=data.index, textprops={'fontsize': FONT_SIZE}, wedgeprops={'linewidth': 3, 'edgecolor': "black"})
        legend = graph_axes.legend(loc=2, prop={'size': FONT_SIZE*1.5})
        graph_fig.set_size_inches(30,30)
        graph_axes.set_ylabel("")
        graph_axes.set_title(f"User percentage of all attachments in #{args[1]}", {'fontsize': FONT_SIZE*3}, fontname="Arial")

        # Change to location of the legend.
        bb = legend.get_bbox_to_anchor().inverse_transformed(graph_axes.transAxes)
        xOffset = 1.25
        bb.x0 = xOffset
        bb.x1 = xOffset
        legend.set_bbox_to_anchor(bb, transform = graph_axes.transAxes)

        print("Saving graph...")
        graph_fig.savefig("allattachments_pie.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        allattachments_pie_png = open("allattachments_pie.png", "rb")
        discord_allattachments_pie_png = discord.File(fp=allattachments_pie_png,filename="allattachments_pie.png")
        await ctx.send(file=discord_allattachments_pie_png)

        allattachments_pie_png.close()

    os.chdir(WORKING_DIRECTORY)

    print(f"Current working directory:\n{os.getcwd()}")

#top5 command-------------------------------------------------------------------
@client.command()
async def top5(ctx):
    print("TOP5-----------------------------------------------------------------")

    serverthere = checkServer(ctx.guild)

    if serverthere != False:
        print("ERROR: Server database does not exist")
        os.chdir(WORKING_DIRECTORY)
        return

    args = getargs(ctx.message.clean_content)

    guild_info = getServer(ctx.guild)
    guild_fields = guild_info.split(">")
    channel_fields = guild_fields[2]

    if len(args) >= 2 and args[1] in channel_fields:

        channel_id = getChannelID(args[1], channel_fields)

        navigatedir(ctx.guild.id,channel_id)

        data = pd.read_csv(f"{channel_id} strippedMessages.csv", dtype="str")

    else:

        navigatedir(ctx.guild.id)

        data = pd.read_csv(f"{ctx.guild.id} strippedMessages.csv", dtype="str")

    cond1 = (len(args) == 2 and args[1] in data.columns)
    cond2 = (len(args) == 3 and args[1] in data.columns and args[2] == "bar")

    cond3 = (len(args) == 3 and args[1] in channel_fields and args[2] in data.columns)
    cond4 = (len(args) == 4 and args[1] in channel_fields and args[2] in data.columns and args[3] == "bar")

    arg_validation = (cond1 or cond2 or cond3 or cond4)

    if arg_validation == False:
        print("ERROR: Invalid args")
        os.chdir(WORKING_DIRECTORY)
        return

    for username in data.columns:
        data[username] = data[username].str[19:]

    FONT_SIZE = 30
    colors = ['#21B3E9','#1D9DCC','#157092','#115974','#0C4357']

    if cond1:
        print("Sending top5 plaintext")

        username = args[1]

        data = data[username].value_counts()[0:5]

        output_str = ""
        number_suffix = ["st","nd","rd","th","th"]
        i = 1
        for message in data.index:
            if len(message) > 250:
                message_str = message[:250] + ". . ."
            else:
                message_str = message

            message_str = message_str.replace('`','')

            output_str += f"**{username}**'s **{str(i) + number_suffix[i-1]}** most typed message is:\n`{message_str}`\nSent **{data[message]}** times!\n"
            i += 1

        await ctx.send(output_str)

    elif cond2:
        print("Creating bar graph...")

        username = args[1]

        data = data[username].value_counts()[0:5][::-1]

        messages = list(data.index)
        messages_range = len(messages)
        for i in range(messages_range):
            if len(messages[i]) > 50:
                messages[i] = messages[i][:50] + ". . ."

        values = data.values

        graph_fig, graph_axes = plt.subplots()
        graph_axes.barh(messages, values, edgecolor="black", linewidth="8",color=colors)

        graph_axes.tick_params(axis='y', which='major', labelsize=FONT_SIZE*2)
        graph_axes.tick_params(axis='x', which='major', labelsize=FONT_SIZE*1.5)
        graph_axes.set_title(f"{username}'s top5 most typed messages in {ctx.guild.name}", size=FONT_SIZE*3, fontname="Arial")
        graph_axes.set_ylabel("Top 5 most typed messages", fontname="Arial", fontsize=int(FONT_SIZE*2))
        graph_axes.set_xlabel("Number of times typed", fontname="Arial", fontsize=int(FONT_SIZE*2))
        graph_fig.set_size_inches(50,20)

        print("Saving graph...")
        graph_fig.savefig("top5_bar.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        top5_bar_png = open("top5_bar.png", "rb")
        discord_top5_bar_png = discord.File(fp=top5_bar_png,filename="top5_bar.png")
        await ctx.send(file=discord_top5_bar_png)

        top5_bar_png.close()

    elif cond3:
        print("Sending top5 plaintext")

        username = args[2]
        channel = args[1]

        data = data[username].value_counts()[0:5]

        output_str = ""
        number_suffix = ["st","nd","rd","th","th"]
        i = 1
        for message in data.index:
            if len(message) > 250:
                message_str = message[:250] + ". . ."
            else:
                message_str = message

            message_str = message_str.replace('`','')

            output_str += f"**{username}**'s **{str(i) + number_suffix[i-1]}** most typed message in channel #{channel} is:\n`{message_str}`\nSent **{data[message]}** times!\n"
            i += 1

        await ctx.send(output_str)

    elif cond4:
        print("Creating bar graph...")

        username = args[2]
        channel = args[1]

        data = data[username].value_counts()[0:5][::-1]

        messages = list(data.index)
        messages_range = len(messages)
        for i in range(messages_range):
            if len(messages[i]) > 50:
                messages[i] = messages[i][:50] + ". . ."

        values = data.values

        graph_fig, graph_axes = plt.subplots()
        graph_axes.barh(messages, values, edgecolor="black", linewidth="8",color=colors)

        graph_axes.tick_params(axis='y', which='major', labelsize=FONT_SIZE*2)
        graph_axes.tick_params(axis='x', which='major', labelsize=FONT_SIZE*1.5)
        graph_axes.set_title(f"{username}'s top5 most typed messages in #{channel}", size=FONT_SIZE*3, fontname="Arial")
        graph_axes.set_ylabel(f"Top 5 most typed messages in #{channel}", fontname="Arial", fontsize=int(FONT_SIZE*2))
        graph_axes.set_xlabel("Number of times typed", fontname="Arial", fontsize=int(FONT_SIZE*2))
        graph_fig.set_size_inches(50,20)

        print("Saving graph...")
        graph_fig.savefig("top5_bar.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        top5_bar_png = open("top5_bar.png", "rb")
        discord_top5_bar_png = discord.File(fp=top5_bar_png,filename="top5_bar.png")
        await ctx.send(file=discord_top5_bar_png)

        top5_bar_png.close()

    os.chdir(WORKING_DIRECTORY)

    print(f"Current working directory:\n{os.getcwd()}")

#allchannels command------------------------------------------------------------
@client.command()
async def allchannels(ctx):
    print("CHANNELS-------------------------------------------------------------")

    serverthere = checkServer(ctx.guild)

    if serverthere != False:
        print("ERROR: Server database does not exist")
        os.chdir(WORKING_DIRECTORY)
        return

    args = getargs(ctx.message.clean_content)

    guild_info = getServer(ctx.guild)
    guild_fields = guild_info.split(">")
    channel_fields = guild_fields[2]

    cond1 = (len(args) == 1)
    cond2 = (len(args) == 2 and args[1] == "bar")
    cond3 = (len(args) == 2 and args[1] == "pie")

    arg_validation = (cond1 or cond2 or cond3)

    if arg_validation == False:
        print("ERROR: Invalid args")
        os.chdir(WORKING_DIRECTORY)
        return

    FONT_SIZE = 30

    channel_df_dict = {}
    channel_fields_list = channel_fields[16:].split(",")
    for channel in channel_fields_list:

        channel_id = channel.split("-")[0]
        navigatedir(ctx.guild.id,channel_id)

        try:
            channel_df_dict[channel_id] = pd.read_csv(f"{channel_id}.csv")
        except:
            print(f"\nTried to read {channel_id}-{getChannelName(channel_id,channel_fields)}.csv, but it was empty\n")
            channel_df_dict[channel_id] = pd.DataFrame()

        os.chdir(WORKING_DIRECTORY)

    navigatedir(ctx.guild.id)

    if cond1:
        print("Sending channels plaintext")

        output_str = ""

        server_total_messages = 0

        for channel_df in channel_df_dict:

            if channel_df_dict[channel_df].empty == False:
                data = channel_df_dict[channel_df]
                data_count = data.count()

                total_messages = 0
                for username in data_count.index:
                    total_messages += data_count[username]

                server_total_messages += total_messages

                output_str += f"**#{getChannelName(channel_df,channel_fields)}** has **{total_messages}** messages!\n"
            else:
                output_str += f"**#{getChannelName(channel_df,channel_fields)}** has **0** messages...\n"

        output_str += f"In total there were **{server_total_messages}** messages sent throughout the entire server!"

        await ctx.send(output_str)

    elif cond2:
        print("Creating bar graph...")

        values = []

        for channel_df in channel_df_dict:

            channel_title = "#" + getChannelName(channel_df,channel_fields)

            if channel_df_dict[channel_df].empty == False:

                data = channel_df_dict[channel_df]
                data_count = data.count()

                total_messages = 0
                for username in data_count.index:
                    total_messages += data_count[username]

                values.append([channel_title, total_messages])
            else:
                values.append([channel_title, 0])

        def sortSecond(input_int):
            return input_int[1]

        values.sort(key=sortSecond, reverse=True)

        channel_names = []
        channel_message_counts = []

        for value_pair in values:
            channel_names.append(value_pair[0])
            channel_message_counts.append(value_pair[1])

        graph_fig, graph_axes = plt.subplots()
        graph_axes.bar(channel_names, channel_message_counts, edgecolor="black", linewidth="5")

        graph_axes.tick_params(axis='y', which='major', labelsize=FONT_SIZE*1)
        graph_axes.tick_params(axis='x', which='major', labelsize=FONT_SIZE*1.5, rotation=65, pad=50)
        graph_axes.set_title(f"{ctx.guild.name} channel message count breakdown", size=FONT_SIZE*3, fontname="Arial")
        graph_axes.set_ylabel("Number of messages sent", fontname="Arial", fontsize=int(FONT_SIZE*2))
        graph_axes.set_xlabel("All channels", fontname="Arial", fontsize=int(FONT_SIZE*2))
        graph_fig.set_size_inches(40,20)

        print("Saving graph...")
        graph_fig.savefig("channels_bar.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        channels_bar_png = open("channels_bar.png", "rb")
        discord_channels_bar_png = discord.File(fp=channels_bar_png,filename="channels_bar.png")
        await ctx.send(file=discord_channels_bar_png)

        channels_bar_png.close()

    elif cond3:
        print("Creating pie graph...")

        values = []

        for channel_df in channel_df_dict:

            if channel_df_dict[channel_df].empty == False:

                data = channel_df_dict[channel_df]
                data_count = data.count()

                total_messages = 0
                for username in data_count.index:
                    total_messages += data_count[username]

                channel_title = "#" + getChannelName(channel_df,channel_fields)
                values.append([channel_title, total_messages])

        def sortSecond(input_int):
            return input_int[1]

        values.sort(key=sortSecond, reverse=True)

        channel_names = []
        channel_message_counts = []
        explode = []

        for value_pair in values:
            channel_names.append(value_pair[0])
            channel_message_counts.append(value_pair[1])
            explode.append(0)

        if len(explode) > 2:
            explode[0] = 0.1

        graph_fig, graph_axes = plt.subplots()
        graph_axes.pie(channel_message_counts, explode=explode, shadow=True, textprops={'fontsize': FONT_SIZE}, wedgeprops={'linewidth': 3, 'edgecolor': "black"}, startangle=90)

        legend = graph_axes.legend(loc=2, labels=channel_names, prop={'size': FONT_SIZE*3})
        graph_axes.set_title(f"{ctx.guild.name} channel message count breakdown ratio", {'fontsize': FONT_SIZE*5}, fontname="Arial")

        bb = legend.get_bbox_to_anchor().inverse_transformed(graph_axes.transAxes)
        xOffset = 1.25
        bb.x0 = xOffset
        bb.x1 = xOffset
        legend.set_bbox_to_anchor(bb, transform = graph_axes.transAxes)

        graph_fig.set_size_inches(30,30)

        print("Saving graph...")
        graph_fig.savefig("channels_pie.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        channels_pie_png = open("channels_pie.png", "rb")
        discord_channels_pie_png = discord.File(fp=channels_pie_png,filename="channels_pie.png")
        await ctx.send(file=discord_channels_pie_png)

        channels_pie_png.close()

    os.chdir(WORKING_DIRECTORY)

    print(f"Current working directory:\n{os.getcwd()}")

#alltime command----------------------------------------------------------------
@client.command()
async def alltime(ctx):
    print("ALLTIME--------------------------------------------------------------")

    serverthere = checkServer(ctx.guild)

    if serverthere != False:
        print("ERROR: Server database does not exist")
        os.chdir(WORKING_DIRECTORY)
        return

    args = getargs(ctx.message.clean_content)

    guild_info = getServer(ctx.guild)
    guild_fields = guild_info.split(">")
    channel_fields = guild_fields[2]

    if len(args) >= 2 and args[1] in channel_fields:

        channel_id = getChannelID(args[1], channel_fields)

        navigatedir(ctx.guild.id,channel_id)

        messagesTime_data = pd.read_csv(f"{channel_id} strippedMessagesDaily.csv", dtype="str",index_col=0)
        attachmentsTime_data = pd.read_csv(f"{channel_id} strippedAttachmentsDaily.csv", dtype="str",index_col=0)

    else:

        navigatedir(ctx.guild.id)

        messagesTime_data = pd.read_csv(f"{ctx.guild.id} strippedMessagesDaily.csv", dtype="str",index_col=0)
        attachmentsTime_data = pd.read_csv(f"{ctx.guild.id} strippedAttachmentsDaily.csv", dtype="str",index_col=0)

    #Server-wide, year/month/day line/bar---------------------------------------
    cond1 = (len(args) == 3 and args[1].lower() == "year" and args[2].lower() == "line")
    cond2 = (len(args) == 3 and args[1].lower() == "year" and args[2].lower() == "bar")
    cond3 = (len(args) == 3 and args[1].lower() == "month" and args[2].lower() == "line")
    cond4 = (len(args) == 3 and args[1].lower() == "month" and args[2].lower() == "bar")
    cond5 = (len(args) == 3 and args[1].lower() == "day" and args[2].lower() == "line")
    cond6 = (len(args) == 3 and args[1].lower() == "day" and args[2].lower() == "bar")

    #Channel-drilldown year/month/day line/bar----------------------------------
    cond7 = (len(args) == 4 and args[1] in channel_fields and args[2].lower() == "year" and args[3].lower() == "line")
    cond8 = (len(args) == 4 and args[1] in channel_fields and args[2].lower() == "year" and args[3].lower() == "bar")
    cond9 = (len(args) == 4 and args[1] in channel_fields and args[2].lower() == "month" and args[3].lower() == "line")
    cond10 = (len(args) == 4 and args[1] in channel_fields and args[2].lower() == "month" and args[3].lower() == "bar")
    cond11 = (len(args) == 4 and args[1] in channel_fields and args[2].lower() == "day" and args[3].lower() == "line")
    cond12 = (len(args) == 4 and args[1] in channel_fields and args[2].lower() == "day" and args[3].lower() == "bar")

    #Username-drilldown year/month/day line/bar---------------------------------
    cond13 = (len(args) == 4 and args[1] in messagesTime_data.columns and args[2].lower() == "year" and args[3].lower() == "line")
    cond14 = (len(args) == 4 and args[1] in messagesTime_data.columns and args[2].lower() == "year" and args[3].lower() == "bar")
    cond15 = (len(args) == 4 and args[1] in messagesTime_data.columns and args[2].lower() == "month" and args[3].lower() == "line")
    cond16 = (len(args) == 4 and args[1] in messagesTime_data.columns and args[2].lower() == "month" and args[3].lower() == "bar")
    cond17 = (len(args) == 4 and args[1] in messagesTime_data.columns and args[2].lower() == "day" and args[3].lower() == "line")
    cond18 = (len(args) == 4 and args[1] in messagesTime_data.columns and args[2].lower() == "day" and args[3].lower() == "bar")

    #Channel-AND-User-drilldown year/month/day line/bar-------------------------
    cond19 = (len(args) == 5 and args[1] in channel_fields and args[2] in messagesTime_data.columns and args[3].lower() == "year" and args[4].lower() == "line")
    cond20 = (len(args) == 5 and args[1] in channel_fields and args[2] in messagesTime_data.columns and args[3].lower() == "year" and args[4].lower() == "bar")
    cond21 = (len(args) == 5 and args[1] in channel_fields and args[2] in messagesTime_data.columns and args[3].lower() == "month" and args[4].lower() == "line")
    cond22 = (len(args) == 5 and args[1] in channel_fields and args[2] in messagesTime_data.columns and args[3].lower() == "month" and args[4].lower() == "bar")
    cond23 = (len(args) == 5 and args[1] in channel_fields and args[2] in messagesTime_data.columns and args[3].lower() == "day" and args[4].lower() == "line")
    cond24 = (len(args) == 5 and args[1] in channel_fields and args[2] in messagesTime_data.columns and args[3].lower() == "day" and args[4].lower() == "bar")


    arg_validation = False
    condition_list = [cond1,cond2,cond3,cond4,cond5,cond6,cond7,cond8,cond9,cond10,cond11,cond12,cond13,cond14,cond15,cond16,cond17,cond18,cond19,cond20,cond21,cond22,cond23,cond24]
    for condition in condition_list:
        if condition == True:
            arg_validation = True
            break

    if arg_validation == False:
        print("ERROR: Invalid args")
        os.chdir(WORKING_DIRECTORY)
        return

    FONT_SIZE = 30

    def listafy(input_str):
        return input_str[1:-1].split('\\n')[:-1]

    #0 = Year, 1 = Month, 2 = Day
    def timeData(input_df, input_timeframe, input_attachment_boolean):

        dataframe_there = (type(input_df) == pd.DataFrame)

        if input_timeframe == 0:
            print("Year drilldown...")

            unique_years = input_df.index.str[0:4].unique()[::-1]
            year_labels = unique_years
            year_values = []
            cumulative_year_values = []
            cumulative_messages_count = 0

            for year in unique_years:
                year_df = input_df[input_df.index.str.match(year)]

                year_messages_count = 0
                for row in year_df.index[::-1]:
                    row_df = year_df.loc[row]

                    if dataframe_there:
                        for username in row_df.index:
                            username_cell_str = row_df[username]

                            if type(username_cell_str) != float:
                                if input_attachment_boolean == True:
                                    attachments_raw = listafy(repr(username_cell_str))

                                    for attachment in attachments_raw[::-1]:
                                        if attachment.endswith("NULL"):
                                            attachments_raw.remove(attachment)

                                    day_messages_count = len(attachments_raw)
                                else:
                                    day_messages_count = len(listafy(repr(username_cell_str)))

                                year_messages_count += day_messages_count
                                cumulative_messages_count += day_messages_count
                    else:
                        username_cell_str = row_df

                        if type(username_cell_str) != float:
                            if input_attachment_boolean == True:
                                attachments_raw = listafy(repr(username_cell_str))

                                for attachment in attachments_raw[::-1]:
                                    if attachment.endswith("NULL"):
                                        attachments_raw.remove(attachment)

                                day_messages_count = len(attachments_raw)
                            else:
                                day_messages_count = len(listafy(repr(username_cell_str)))

                            year_messages_count += day_messages_count
                            cumulative_messages_count += day_messages_count

                year_values.append(year_messages_count)
                cumulative_year_values.append(cumulative_messages_count)

            return [year_labels, year_values, cumulative_year_values]

        elif input_timeframe == 1:
            print("Month drilldown...")

            unique_months = input_df.index.str[0:7].unique()[::-1]
            month_labels = unique_months
            month_values = []
            cumulative_month_values = []
            cumulative_messages_count = 0

            for month in unique_months:
                month_df = input_df[input_df.index.str.match(month)]

                month_messages_count = 0
                for row in month_df.index[::-1]:
                    row_df = month_df.loc[row]

                    if dataframe_there:
                        for username in row_df.index:
                            username_cell_str = row_df[username]

                            if type(username_cell_str) != float:
                                if input_attachment_boolean == True:
                                    attachments_raw = listafy(repr(username_cell_str))

                                    for attachment in attachments_raw[::-1]:
                                        if attachment.endswith("NULL"):
                                            attachments_raw.remove(attachment)

                                    day_messages_count = len(attachments_raw)
                                else:
                                    day_messages_count = len(listafy(repr(username_cell_str)))

                                month_messages_count += day_messages_count
                                cumulative_messages_count += day_messages_count
                    else:
                        username_cell_str = row_df

                        if type(username_cell_str) != float:
                            if input_attachment_boolean == True:
                                attachments_raw = listafy(repr(username_cell_str))

                                for attachment in attachments_raw[::-1]:
                                    if attachment.endswith("NULL"):
                                        attachments_raw.remove(attachment)

                                day_messages_count = len(attachments_raw)
                            else:
                                day_messages_count = len(listafy(repr(username_cell_str)))

                            month_messages_count += day_messages_count
                            cumulative_messages_count += day_messages_count

                month_values.append(month_messages_count)
                cumulative_month_values.append(cumulative_messages_count)

            return [month_labels, month_values, cumulative_month_values]

        elif input_timeframe == 2:
            print("Day drilldown...")

            day_labels = input_df.index[::-1]
            day_values = []
            cumulative_day_values = []
            cumulative_messages_count = 0

            for row in input_df.index[::-1]:
                row_df = input_df.loc[row]

                day_messages_count = 0
                if dataframe_there:
                    for username in row_df.index:
                        username_cell_str = row_df[username]

                        if type(username_cell_str) != float:
                            if input_attachment_boolean == True:
                                attachments_raw = listafy(repr(username_cell_str))

                                for attachment in attachments_raw[::-1]:
                                    if attachment.endswith("NULL"):
                                        attachments_raw.remove(attachment)

                                day_messages_count += len(attachments_raw)

                            else:
                                day_messages_count += len(listafy(repr(username_cell_str)))

                            cumulative_messages_count += day_messages_count
                else:
                    username_cell_str = row_df

                    if type(username_cell_str) != float:
                        if input_attachment_boolean == True:
                            attachments_raw = listafy(repr(username_cell_str))

                            for attachment in attachments_raw[::-1]:
                                if attachment.endswith("NULL"):
                                    attachments_raw.remove(attachment)

                            day_messages_count += len(attachments_raw)

                        else:
                            day_messages_count += len(listafy(repr(username_cell_str)))

                        cumulative_messages_count += day_messages_count

                day_values.append(day_messages_count)
                cumulative_day_values.append(cumulative_messages_count)

            return [day_labels, day_values, cumulative_day_values]

    if cond1:
        print("Creating line graph...")

        messageData = timeData(messagesTime_data,0, False)
        attachmentData = timeData(attachmentsTime_data,0, True)

        graph_fig, graph_axes = plt.subplots(4,1)

        graph_axes[0].plot(messageData[0], messageData[1], linewidth=3, marker='o', markersize=10, color="red")
        graph_axes[0].tick_params(axis="x", which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[0].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[0].grid()
        graph_axes[0].set_title("Messages per Year", fontsize=FONT_SIZE, pad=25)

        graph_axes[1].plot(messageData[0], messageData[2], linewidth=3, marker='o', markersize=10, color="red")
        graph_axes[1].tick_params(axis="x", which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[1].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[1].grid()
        graph_axes[1].set_title("Cumulative Messages per Year", fontsize=FONT_SIZE, pad=25)

        graph_axes[2].plot(attachmentData[0], attachmentData[1], linewidth=3, marker='o', markersize=10, color="blue")
        graph_axes[2].tick_params(axis='x', which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[2].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[2].grid()
        graph_axes[2].set_title("Attachments per Year", fontsize=FONT_SIZE, pad=25)

        graph_axes[3].plot(attachmentData[0], attachmentData[2], linewidth=3, marker='o', markersize=10, color="blue")
        graph_axes[3].tick_params(axis='x', which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[3].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[3].grid()
        graph_axes[3].set_title("Cumulative Attachments per Year", fontsize=FONT_SIZE, pad=25)

        graph_fig.set_size_inches(45,30)
        plt.subplots_adjust(hspace=0.3)
        plt.suptitle(f"Messages & Attachments sent per Year in {ctx.guild.name}", fontsize=FONT_SIZE*2)

        print("Saving graph...")
        graph_fig.savefig("alltime_year_line.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        alltime_year_line_png = open("alltime_year_line.png", "rb")
        discord_alltime_year_line_png = discord.File(fp=alltime_year_line_png,filename="alltime_year_line.png")
        await ctx.send(file=discord_alltime_year_line_png)

        alltime_year_line_png.close()

    elif cond2:
        print("Creating bar graph...")

        messageData = timeData(messagesTime_data,0, False)
        attachmentData = timeData(attachmentsTime_data,0, True)

        graph_fig, graph_axes = plt.subplots(2,2)

        graph_axes[0,0].bar(messageData[0], messageData[1], color="red", width=0.5)
        graph_axes[0,0].tick_params(axis="x", which='major', rotation=0, labelsize=FONT_SIZE)
        graph_axes[0,0].tick_params(axis="y", which='major', labelsize=FONT_SIZE)
        graph_axes[0,0].grid(axis="y")
        graph_axes[0,0].set_title("Messages per Year", fontsize=FONT_SIZE*2, pad=25)

        graph_axes[1,0].bar(messageData[0], messageData[2], color="red", width=0.5)
        graph_axes[1,0].tick_params(axis="x", which='major', rotation=0, labelsize=FONT_SIZE)
        graph_axes[1,0].tick_params(axis="y", which='major', labelsize=FONT_SIZE)
        graph_axes[1,0].grid(axis="y")
        graph_axes[1,0].set_title("Cumulative Messages per Year", fontsize=FONT_SIZE*2, pad=25)

        graph_axes[0,1].bar(attachmentData[0], attachmentData[1], color="blue", width=0.5)
        graph_axes[0,1].tick_params(axis='x', which='major', rotation=0, labelsize=FONT_SIZE)
        graph_axes[0,1].tick_params(axis="y", which='major', labelsize=FONT_SIZE)
        graph_axes[0,1].grid(axis="y")
        graph_axes[0,1].set_title("Attachments per Year", fontsize=FONT_SIZE*2, pad=25)

        graph_axes[1,1].bar(attachmentData[0], attachmentData[2], color="blue", width=0.5)
        graph_axes[1,1].tick_params(axis='x', which='major', rotation=0, labelsize=FONT_SIZE)
        graph_axes[1,1].tick_params(axis="y", which='major', labelsize=FONT_SIZE)
        graph_axes[1,1].grid(axis="y")
        graph_axes[1,1].set_title("Cumulative Attachments per Year", fontsize=FONT_SIZE*2, pad=25)

        graph_fig.set_size_inches(100,50)
        plt.subplots_adjust(hspace=0.3)
        plt.suptitle(f"Messages & Attachments sent per Year in {ctx.guild.name}", fontsize=FONT_SIZE*4)

        print("Saving graph...")
        graph_fig.savefig("alltime_year_bar.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        alltime_year_bar_png = open("alltime_year_bar.png", "rb")
        discord_alltime_year_bar_png = discord.File(fp=alltime_year_bar_png,filename="alltime_year_bar.png")
        await ctx.send(file=discord_alltime_year_bar_png)

        alltime_year_bar_png.close()

    elif cond3:
        print("Creating line graph...")

        messageData = timeData(messagesTime_data,1, False)
        attachmentData = timeData(attachmentsTime_data,1, True)

        graph_fig, graph_axes = plt.subplots(4,1)

        graph_axes[0].plot(messageData[0], messageData[1], linewidth=3, marker='o', markersize=10, color="red")
        graph_axes[0].tick_params(axis="x", which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[0].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[0].grid()
        graph_axes[0].set_title("Messages per Month", fontsize=FONT_SIZE, pad=25)

        graph_axes[1].plot(messageData[0], messageData[2], linewidth=3, marker='o', markersize=10, color="red")
        graph_axes[1].tick_params(axis="x", which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[1].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[1].grid()
        graph_axes[1].set_title("Cumulative Messages per Month", fontsize=FONT_SIZE, pad=25)

        graph_axes[2].plot(attachmentData[0], attachmentData[1], linewidth=3, marker='o', markersize=10, color="blue")
        graph_axes[2].tick_params(axis='x', which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[2].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[2].grid()
        graph_axes[2].set_title("Attachments per Month", fontsize=FONT_SIZE, pad=25)

        graph_axes[3].plot(attachmentData[0], attachmentData[2], linewidth=3, marker='o', markersize=10, color="blue")
        graph_axes[3].tick_params(axis='x', which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[3].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[3].grid()
        graph_axes[3].set_title("Cumulative Attachments per Month", fontsize=FONT_SIZE, pad=25)

        graph_fig.set_size_inches(45,30)
        plt.subplots_adjust(hspace=0.3)
        plt.suptitle(f"Messages & Attachments sent per Month in {ctx.guild.name}", fontsize=FONT_SIZE*2)

        print("Saving graph...")
        graph_fig.savefig("alltime_month_line.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        alltime_month_line_png = open("alltime_month_line.png", "rb")
        discord_alltime_month_line_png = discord.File(fp=alltime_month_line_png,filename="alltime_month_line.png")
        await ctx.send(file=discord_alltime_month_line_png)

        alltime_month_line_png.close()

    elif cond4:
        print("Creating bar graph...")

        messageData = timeData(messagesTime_data,1, False)
        attachmentData = timeData(attachmentsTime_data,1, True)

        graph_fig, graph_axes = plt.subplots(2,2)

        graph_axes[0,0].bar(messageData[0], messageData[1], color="red", width=0.5)
        graph_axes[0,0].tick_params(axis="x", which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[0,0].tick_params(axis="y", which='major', labelsize=FONT_SIZE*2)
        graph_axes[0,0].grid(axis="y")
        graph_axes[0,0].set_title("Messages per Month", fontsize=FONT_SIZE*3, pad=25)

        graph_axes[1,0].bar(messageData[0], messageData[2], color="red", width=0.5)
        graph_axes[1,0].tick_params(axis="x", which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[1,0].tick_params(axis="y", which='major', labelsize=FONT_SIZE*2)
        graph_axes[1,0].grid(axis="y")
        graph_axes[1,0].set_title("Cumulative Messages per Month", fontsize=FONT_SIZE*3, pad=25)

        graph_axes[0,1].bar(attachmentData[0], attachmentData[1], color="blue", width=0.5)
        graph_axes[0,1].tick_params(axis='x', which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[0,1].tick_params(axis="y", which='major', labelsize=FONT_SIZE*2)
        graph_axes[0,1].grid(axis="y")
        graph_axes[0,1].set_title("Attachments per Month", fontsize=FONT_SIZE*3, pad=25)

        graph_axes[1,1].bar(attachmentData[0], attachmentData[2], color="blue", width=0.5)
        graph_axes[1,1].tick_params(axis='x', which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[1,1].tick_params(axis="y", which='major', labelsize=FONT_SIZE*2)
        graph_axes[1,1].grid(axis="y")
        graph_axes[1,1].set_title("Cumulative Attachments per Month", fontsize=FONT_SIZE*3, pad=25)

        graph_fig.set_size_inches(150,50)
        plt.subplots_adjust(hspace=0.3)
        plt.suptitle(f"Messages & Attachments sent per Month in {ctx.guild.name}", fontsize=FONT_SIZE*6)

        print("Saving graph...")
        graph_fig.savefig("alltime_month_bar.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        alltime_month_bar_png = open("alltime_month_bar.png", "rb")
        discord_alltime_month_bar_png = discord.File(fp=alltime_month_bar_png,filename="alltime_month_bar.png")
        await ctx.send(file=discord_alltime_month_bar_png)

        alltime_month_bar_png.close()

    elif cond5:
        print("Creating line graph...")

        messageData = timeData(messagesTime_data,2, False)
        attachmentData = timeData(attachmentsTime_data,2, True)

        graph_fig, graph_axes = plt.subplots(4,1)

        graph_axes[0].plot(messageData[0], messageData[1], linewidth=1, marker='o', markersize=5, color="red")
        graph_axes[0].tick_params(axis="x", which='major', rotation=0, labelsize=0)
        graph_axes[0].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[0].grid()
        graph_axes[0].set_title("Messages per Day", fontsize=FONT_SIZE, pad=25)

        graph_axes[1].plot(messageData[0], messageData[2], linewidth=1, marker='o', markersize=5, color="red")
        graph_axes[1].tick_params(axis="x", which='major', rotation=0, labelsize=0)
        graph_axes[1].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[1].grid()
        graph_axes[1].set_title("Cumulative Messages per Day", fontsize=FONT_SIZE, pad=25)

        graph_axes[2].plot(attachmentData[0], attachmentData[1], linewidth=1, marker='o', markersize=5, color="blue")
        graph_axes[2].tick_params(axis='x', which='major', rotation=0, labelsize=0)
        graph_axes[2].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[2].grid()
        graph_axes[2].set_title("Attachments per Day", fontsize=FONT_SIZE, pad=25)

        graph_axes[3].plot(attachmentData[0], attachmentData[2], linewidth=1, marker='o', markersize=5, color="blue")
        graph_axes[3].tick_params(axis='x', which='major', rotation=0, labelsize=0)
        graph_axes[3].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[3].grid()
        graph_axes[3].set_title("Cumulative Attachments per Day", fontsize=FONT_SIZE, pad=25)

        graph_fig.set_size_inches(45,30)
        plt.subplots_adjust(hspace=0.3)
        plt.suptitle(f"Messages & Attachments sent per Day in {ctx.guild.name}", fontsize=FONT_SIZE*2)

        print("Saving graph...")
        graph_fig.savefig("alltime_day_line.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        alltime_day_line_png = open("alltime_day_line.png", "rb")
        discord_alltime_day_line_png = discord.File(fp=alltime_day_line_png,filename="alltime_day_line.png")
        await ctx.send(file=discord_alltime_day_line_png)

        alltime_day_line_png.close()

    elif cond6:
        print("Creating bar graph...")

        messageData = timeData(messagesTime_data,2, False)
        attachmentData = timeData(attachmentsTime_data,2, True)

        graph_fig, graph_axes = plt.subplots(2,2)

        graph_axes[0,0].bar(messageData[0], messageData[1], color="red", width=0.5)
        graph_axes[0,0].tick_params(axis="x", which='major', rotation=0, labelsize=0)
        graph_axes[0,0].tick_params(axis="y", which='major', labelsize=FONT_SIZE*2)
        graph_axes[0,0].grid(axis="y")
        graph_axes[0,0].set_title("Messages per day", fontsize=FONT_SIZE*3, pad=25)

        graph_axes[1,0].bar(messageData[0], messageData[2], color="red", width=0.5)
        graph_axes[1,0].tick_params(axis="x", which='major', rotation=0, labelsize=0)
        graph_axes[1,0].tick_params(axis="y", which='major', labelsize=FONT_SIZE*2)
        graph_axes[1,0].grid(axis="y")
        graph_axes[1,0].set_title("Cumulative Messages per Day", fontsize=FONT_SIZE*3, pad=25)

        graph_axes[0,1].bar(attachmentData[0], attachmentData[1], color="blue", width=0.5)
        graph_axes[0,1].tick_params(axis='x', which='major', rotation=0, labelsize=0)
        graph_axes[0,1].tick_params(axis="y", which='major', labelsize=FONT_SIZE*2)
        graph_axes[0,1].grid(axis="y")
        graph_axes[0,1].set_title("Attachments per Day", fontsize=FONT_SIZE*3, pad=25)

        graph_axes[1,1].bar(attachmentData[0], attachmentData[2], color="blue", width=0.5)
        graph_axes[1,1].tick_params(axis='x', which='major', rotation=0, labelsize=0)
        graph_axes[1,1].tick_params(axis="y", which='major', labelsize=FONT_SIZE*2)
        graph_axes[1,1].grid(axis="y")
        graph_axes[1,1].set_title("Cumulative Attachments per Day", fontsize=FONT_SIZE*3, pad=25)

        graph_fig.set_size_inches(150,50)
        plt.subplots_adjust(hspace=0.3)
        plt.suptitle(f"Messages & Attachments sent per Day in {ctx.guild.name}", fontsize=FONT_SIZE*6)

        print("Saving graph...")
        graph_fig.savefig("alltime_day_bar.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        alltime_day_bar_png = open("alltime_day_bar.png", "rb")
        discord_alltime_day_bar_png = discord.File(fp=alltime_day_bar_png,filename="alltime_day_bar.png")
        await ctx.send(file=discord_alltime_day_bar_png)

        alltime_day_bar_png.close()

    elif cond7:
        print("Creating line graph...")

        messageData = timeData(messagesTime_data,0, False)
        attachmentData = timeData(attachmentsTime_data,0, True)

        graph_fig, graph_axes = plt.subplots(4,1)

        graph_axes[0].plot(messageData[0], messageData[1], linewidth=3, marker='o', markersize=10, color="red")
        graph_axes[0].tick_params(axis="x", which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[0].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[0].grid()
        graph_axes[0].set_title("Messages per Year", fontsize=FONT_SIZE, pad=25)

        graph_axes[1].plot(messageData[0], messageData[2], linewidth=3, marker='o', markersize=10, color="red")
        graph_axes[1].tick_params(axis="x", which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[1].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[1].grid()
        graph_axes[1].set_title("Cumulative Messages per Year", fontsize=FONT_SIZE, pad=25)

        graph_axes[2].plot(attachmentData[0], attachmentData[1], linewidth=3, marker='o', markersize=10, color="blue")
        graph_axes[2].tick_params(axis='x', which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[2].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[2].grid()
        graph_axes[2].set_title("Attachments per Year", fontsize=FONT_SIZE, pad=25)

        graph_axes[3].plot(attachmentData[0], attachmentData[2], linewidth=3, marker='o', markersize=10, color="blue")
        graph_axes[3].tick_params(axis='x', which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[3].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[3].grid()
        graph_axes[3].set_title("Cumulative Attachments per Year", fontsize=FONT_SIZE, pad=25)

        graph_fig.set_size_inches(45,30)
        plt.subplots_adjust(hspace=0.3)
        plt.suptitle(f"Messages & Attachments sent per Year in #{args[1]}", fontsize=FONT_SIZE*2)

        print("Saving graph...")
        graph_fig.savefig("alltime_year_channel_line.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        alltime_year_channel_line_png = open("alltime_year_channel_line.png", "rb")
        discord_alltime_year_channel_line_png = discord.File(fp=alltime_year_channel_line_png,filename="alltime_year_channel_line.png")
        await ctx.send(file=discord_alltime_year_channel_line_png)

        alltime_year_channel_line_png.close()

    elif cond8:
        print("Creating bar graph...")

        messageData = timeData(messagesTime_data,0, False)
        attachmentData = timeData(attachmentsTime_data,0, True)

        graph_fig, graph_axes = plt.subplots(2,2)

        graph_axes[0,0].bar(messageData[0], messageData[1], color="red", width=0.5)
        graph_axes[0,0].tick_params(axis="x", which='major', rotation=0, labelsize=FONT_SIZE)
        graph_axes[0,0].tick_params(axis="y", which='major', labelsize=FONT_SIZE)
        graph_axes[0,0].grid(axis="y")
        graph_axes[0,0].set_title("Messages per Year", fontsize=FONT_SIZE*2, pad=25)

        graph_axes[1,0].bar(messageData[0], messageData[2], color="red", width=0.5)
        graph_axes[1,0].tick_params(axis="x", which='major', rotation=0, labelsize=FONT_SIZE)
        graph_axes[1,0].tick_params(axis="y", which='major', labelsize=FONT_SIZE)
        graph_axes[1,0].grid(axis="y")
        graph_axes[1,0].set_title("Cumulative Messages per Year", fontsize=FONT_SIZE*2, pad=25)

        graph_axes[0,1].bar(attachmentData[0], attachmentData[1], color="blue", width=0.5)
        graph_axes[0,1].tick_params(axis='x', which='major', rotation=0, labelsize=FONT_SIZE)
        graph_axes[0,1].tick_params(axis="y", which='major', labelsize=FONT_SIZE)
        graph_axes[0,1].grid(axis="y")
        graph_axes[0,1].set_title("Attachments per Year", fontsize=FONT_SIZE*2, pad=25)

        graph_axes[1,1].bar(attachmentData[0], attachmentData[2], color="blue", width=0.5)
        graph_axes[1,1].tick_params(axis='x', which='major', rotation=0, labelsize=FONT_SIZE)
        graph_axes[1,1].tick_params(axis="y", which='major', labelsize=FONT_SIZE)
        graph_axes[1,1].grid(axis="y")
        graph_axes[1,1].set_title("Cumulative Attachments per Year", fontsize=FONT_SIZE*2, pad=25)

        graph_fig.set_size_inches(100,50)
        plt.subplots_adjust(hspace=0.3)
        plt.suptitle(f"Messages & Attachments sent per Year in #{args[1]}", fontsize=FONT_SIZE*4)

        print("Saving graph...")
        graph_fig.savefig("alltime_year_channel_bar.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        alltime_year_channel_bar_png = open("alltime_year_channel_bar.png.png", "rb")
        discord_alltime_year_channel_bar_png = discord.File(fp=alltime_year_channel_bar_png,filename="alltime_year_channel_bar.png")
        await ctx.send(file=discord_alltime_year_channel_bar_png)

        alltime_year_channel_bar_png.close()

    elif cond9:
        print("Creating line graph...")

        messageData = timeData(messagesTime_data,1, False)
        attachmentData = timeData(attachmentsTime_data,1, True)

        graph_fig, graph_axes = plt.subplots(4,1)

        graph_axes[0].plot(messageData[0], messageData[1], linewidth=3, marker='o', markersize=10, color="red")
        graph_axes[0].tick_params(axis="x", which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[0].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[0].grid()
        graph_axes[0].set_title("Messages per Month", fontsize=FONT_SIZE, pad=25)

        graph_axes[1].plot(messageData[0], messageData[2], linewidth=3, marker='o', markersize=10, color="red")
        graph_axes[1].tick_params(axis="x", which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[1].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[1].grid()
        graph_axes[1].set_title("Cumulative Messages per Month", fontsize=FONT_SIZE, pad=25)

        graph_axes[2].plot(attachmentData[0], attachmentData[1], linewidth=3, marker='o', markersize=10, color="blue")
        graph_axes[2].tick_params(axis='x', which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[2].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[2].grid()
        graph_axes[2].set_title("Attachments per Month", fontsize=FONT_SIZE, pad=25)

        graph_axes[3].plot(attachmentData[0], attachmentData[2], linewidth=3, marker='o', markersize=10, color="blue")
        graph_axes[3].tick_params(axis='x', which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[3].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[3].grid()
        graph_axes[3].set_title("Cumulative Attachments per Month", fontsize=FONT_SIZE, pad=25)

        graph_fig.set_size_inches(45,30)
        plt.subplots_adjust(hspace=0.3)
        plt.suptitle(f"Messages & Attachments sent per Month in #{args[1]}", fontsize=FONT_SIZE*2)

        print("Saving graph...")
        graph_fig.savefig("alltime_month_channel_line.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        alltime_month_channel_line_png = open("alltime_month_channel_line.png", "rb")
        discord_alltime_month_channel_line_png = discord.File(fp=alltime_month_channel_line_png,filename="alltime_month_channel_line.png")
        await ctx.send(file=discord_alltime_month_channel_line_png)

        alltime_month_channel_line_png.close()

    elif cond10:
        print("Creating bar graph...")

        messageData = timeData(messagesTime_data,1, False)
        attachmentData = timeData(attachmentsTime_data,1, True)

        graph_fig, graph_axes = plt.subplots(2,2)

        graph_axes[0,0].bar(messageData[0], messageData[1], color="red", width=0.5)
        graph_axes[0,0].tick_params(axis="x", which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[0,0].tick_params(axis="y", which='major', labelsize=FONT_SIZE*2)
        graph_axes[0,0].grid(axis="y")
        graph_axes[0,0].set_title("Messages per Month", fontsize=FONT_SIZE*4, pad=25)

        graph_axes[1,0].bar(messageData[0], messageData[2], color="red", width=0.5)
        graph_axes[1,0].tick_params(axis="x", which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[1,0].tick_params(axis="y", which='major', labelsize=FONT_SIZE*2)
        graph_axes[1,0].grid(axis="y")
        graph_axes[1,0].set_title("Cumulative Messages per Month", fontsize=FONT_SIZE*4, pad=25)

        graph_axes[0,1].bar(attachmentData[0], attachmentData[1], color="blue", width=0.5)
        graph_axes[0,1].tick_params(axis='x', which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[0,1].tick_params(axis="y", which='major', labelsize=FONT_SIZE*2)
        graph_axes[0,1].grid(axis="y")
        graph_axes[0,1].set_title("Attachments per Month", fontsize=FONT_SIZE*4, pad=25)

        graph_axes[1,1].bar(attachmentData[0], attachmentData[2], color="blue", width=0.5)
        graph_axes[1,1].tick_params(axis='x', which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[1,1].tick_params(axis="y", which='major', labelsize=FONT_SIZE*2)
        graph_axes[1,1].grid(axis="y")
        graph_axes[1,1].set_title("Cumulative Attachments per Month", fontsize=FONT_SIZE*4, pad=25)

        graph_fig.set_size_inches(150,50)
        plt.subplots_adjust(hspace=0.3)
        plt.suptitle(f"Messages & Attachments sent per Month in #{args[1]}", fontsize=FONT_SIZE*6)

        print("Saving graph...")
        graph_fig.savefig("alltime_month_channel_bar.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        alltime_month_channel_bar_png = open("alltime_month_channel_bar.png", "rb")
        discord_alltime_month_channel_bar_png = discord.File(fp=alltime_month_channel_bar_png,filename="alltime_month_channel_bar.png")
        await ctx.send(file=discord_alltime_month_channel_bar_png)

        alltime_month_channel_bar_png.close()

    elif cond11:
        print("Creating line graph...")

        messageData = timeData(messagesTime_data,2, False)
        attachmentData = timeData(attachmentsTime_data,2, True)

        graph_fig, graph_axes = plt.subplots(4,1)

        graph_axes[0].plot(messageData[0], messageData[1], linewidth=1, marker='o', markersize=5, color="red")
        graph_axes[0].tick_params(axis="x", which='major', rotation=0, labelsize=0)
        graph_axes[0].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[0].grid()
        graph_axes[0].set_title("Messages per Day", fontsize=FONT_SIZE, pad=25)

        graph_axes[1].plot(messageData[0], messageData[2], linewidth=1, marker='o', markersize=5, color="red")
        graph_axes[1].tick_params(axis="x", which='major', rotation=0, labelsize=0)
        graph_axes[1].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[1].grid()
        graph_axes[1].set_title("Cumulative Messages per Day", fontsize=FONT_SIZE, pad=25)

        graph_axes[2].plot(attachmentData[0], attachmentData[1], linewidth=1, marker='o', markersize=5, color="blue")
        graph_axes[2].tick_params(axis='x', which='major', rotation=0, labelsize=0)
        graph_axes[2].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[2].grid()
        graph_axes[2].set_title("Attachments per Day", fontsize=FONT_SIZE, pad=25)

        graph_axes[3].plot(attachmentData[0], attachmentData[2], linewidth=1, marker='o', markersize=5, color="blue")
        graph_axes[3].tick_params(axis='x', which='major', rotation=0, labelsize=0)
        graph_axes[3].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[3].grid()
        graph_axes[3].set_title("Cumulative Attachments per Day", fontsize=FONT_SIZE, pad=25)

        graph_fig.set_size_inches(45,30)
        plt.subplots_adjust(hspace=0.3)
        plt.suptitle(f"Messages & Attachments sent per Day in #{args[1]}", fontsize=FONT_SIZE*2)

        print("Saving graph...")
        graph_fig.savefig("alltime_day_channel_line.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        alltime_day_channel_line_png = open("alltime_day_channel_line.png", "rb")
        discord_alltime_day_channel_line_png = discord.File(fp=alltime_day_channel_line_png,filename="alltime_day_channel_line.png")
        await ctx.send(file=discord_alltime_day_channel_line_png)

        alltime_day_channel_line_png.close()

    elif cond12:
        print("Creating bar graph...")

        messageData = timeData(messagesTime_data,2, False)
        attachmentData = timeData(attachmentsTime_data,2, True)

        graph_fig, graph_axes = plt.subplots(2,2)

        graph_axes[0,0].bar(messageData[0], messageData[1], color="red", width=0.5)
        graph_axes[0,0].tick_params(axis="x", which='major', rotation=0, labelsize=0)
        graph_axes[0,0].tick_params(axis="y", which='major', labelsize=FONT_SIZE*2)
        graph_axes[0,0].grid(axis="y")
        graph_axes[0,0].set_title("Messages per day", fontsize=FONT_SIZE*3, pad=25)

        graph_axes[1,0].bar(messageData[0], messageData[2], color="red", width=0.5)
        graph_axes[1,0].tick_params(axis="x", which='major', rotation=0, labelsize=0)
        graph_axes[1,0].tick_params(axis="y", which='major', labelsize=FONT_SIZE*2)
        graph_axes[1,0].grid(axis="y")
        graph_axes[1,0].set_title("Cumulative Messages per Day", fontsize=FONT_SIZE*3, pad=25)

        graph_axes[0,1].bar(attachmentData[0], attachmentData[1], color="blue", width=0.5)
        graph_axes[0,1].tick_params(axis='x', which='major', rotation=0, labelsize=0)
        graph_axes[0,1].tick_params(axis="y", which='major', labelsize=FONT_SIZE*2)
        graph_axes[0,1].grid(axis="y")
        graph_axes[0,1].set_title("Attachments per Day", fontsize=FONT_SIZE*3, pad=25)

        graph_axes[1,1].bar(attachmentData[0], attachmentData[2], color="blue", width=0.5)
        graph_axes[1,1].tick_params(axis='x', which='major', rotation=0, labelsize=0)
        graph_axes[1,1].tick_params(axis="y", which='major', labelsize=FONT_SIZE*2)
        graph_axes[1,1].grid(axis="y")
        graph_axes[1,1].set_title("Cumulative Attachments per Day", fontsize=FONT_SIZE*3, pad=25)

        graph_fig.set_size_inches(150,50)
        plt.subplots_adjust(hspace=0.3)
        plt.suptitle(f"Messages & Attachments sent per Day in #{args[1]}", fontsize=FONT_SIZE*6)

        print("Saving graph...")
        graph_fig.savefig("alltime_day_channel_bar.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        alltime_day_channel_bar_png = open("alltime_day_channel_bar.png", "rb")
        discord_alltime_day_channel_bar_png = discord.File(fp=alltime_day_channel_bar_png,filename="alltime_day_channel_bar.png")
        await ctx.send(file=discord_alltime_day_channel_bar_png)

        alltime_day_channel_bar_png.close()

    elif cond13:
        print("Creating line graph...")

        username = args[1]

        messageData = timeData(messagesTime_data[username],0, False)
        attachmentData = timeData(attachmentsTime_data[username],0, True)

        graph_fig, graph_axes = plt.subplots(4,1)

        graph_axes[0].plot(messageData[0], messageData[1], linewidth=3, marker='o', markersize=10, color="red")
        graph_axes[0].tick_params(axis="x", which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[0].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[0].grid()
        graph_axes[0].set_title("Messages per Year", fontsize=FONT_SIZE, pad=25)

        graph_axes[1].plot(messageData[0], messageData[2], linewidth=3, marker='o', markersize=10, color="red")
        graph_axes[1].tick_params(axis="x", which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[1].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[1].grid()
        graph_axes[1].set_title("Cumulative Messages per Year", fontsize=FONT_SIZE, pad=25)

        graph_axes[2].plot(attachmentData[0], attachmentData[1], linewidth=3, marker='o', markersize=10, color="blue")
        graph_axes[2].tick_params(axis='x', which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[2].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[2].grid()
        graph_axes[2].set_title("Attachments per Year", fontsize=FONT_SIZE, pad=25)

        graph_axes[3].plot(attachmentData[0], attachmentData[2], linewidth=3, marker='o', markersize=10, color="blue")
        graph_axes[3].tick_params(axis='x', which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[3].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[3].grid()
        graph_axes[3].set_title("Cumulative Attachments per Year", fontsize=FONT_SIZE, pad=25)

        graph_fig.set_size_inches(45,30)
        plt.subplots_adjust(hspace=0.3)
        plt.suptitle(f"Messages & Attachments sent per Year in {ctx.guild.name} by {username}", fontsize=FONT_SIZE*2)

        print("Saving graph...")
        graph_fig.savefig("alltime_year_username_line.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        alltime_year_username_line_png = open("alltime_year_username_line.png", "rb")
        discord_alltime_year_username_line_png = discord.File(fp=alltime_year_username_line_png,filename="alltime_year_username_line.png")
        await ctx.send(file=discord_alltime_year_username_line_png)

        alltime_year_username_line_png.close()

    elif cond14:
        print("Creating bar graph...")

        username = args[1]

        messageData = timeData(messagesTime_data[username],0, False)
        attachmentData = timeData(attachmentsTime_data[username],0, True)

        graph_fig, graph_axes = plt.subplots(2,2)

        graph_axes[0,0].bar(messageData[0], messageData[1], color="red", width=0.5)
        graph_axes[0,0].tick_params(axis="x", which='major', rotation=0, labelsize=FONT_SIZE)
        graph_axes[0,0].tick_params(axis="y", which='major', labelsize=FONT_SIZE)
        graph_axes[0,0].grid(axis="y")
        graph_axes[0,0].set_title("Messages per Year", fontsize=FONT_SIZE*2, pad=25)

        graph_axes[1,0].bar(messageData[0], messageData[2], color="red", width=0.5)
        graph_axes[1,0].tick_params(axis="x", which='major', rotation=0, labelsize=FONT_SIZE)
        graph_axes[1,0].tick_params(axis="y", which='major', labelsize=FONT_SIZE)
        graph_axes[1,0].grid(axis="y")
        graph_axes[1,0].set_title("Cumulative Messages per Year", fontsize=FONT_SIZE*2, pad=25)

        graph_axes[0,1].bar(attachmentData[0], attachmentData[1], color="blue", width=0.5)
        graph_axes[0,1].tick_params(axis='x', which='major', rotation=0, labelsize=FONT_SIZE)
        graph_axes[0,1].tick_params(axis="y", which='major', labelsize=FONT_SIZE)
        graph_axes[0,1].grid(axis="y")
        graph_axes[0,1].set_title("Attachments per Year", fontsize=FONT_SIZE*2, pad=25)

        graph_axes[1,1].bar(attachmentData[0], attachmentData[2], color="blue", width=0.5)
        graph_axes[1,1].tick_params(axis='x', which='major', rotation=0, labelsize=FONT_SIZE)
        graph_axes[1,1].tick_params(axis="y", which='major', labelsize=FONT_SIZE)
        graph_axes[1,1].grid(axis="y")
        graph_axes[1,1].set_title("Cumulative Attachments per Year", fontsize=FONT_SIZE*2, pad=25)

        graph_fig.set_size_inches(100,50)
        plt.subplots_adjust(hspace=0.3)
        plt.suptitle(f"Messages & Attachments sent per Year in {ctx.guild.name} by {username}", fontsize=FONT_SIZE*4)

        print("Saving graph...")
        graph_fig.savefig("alltime_year_username_bar.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        alltime_year_username_bar_png = open("alltime_year_username_bar.png", "rb")
        discord_alltime_year_username_bar_png = discord.File(fp=alltime_year_username_bar_png,filename="alltime_year_username_bar.png")
        await ctx.send(file=discord_alltime_year_username_bar_png)

        alltime_year_username_bar_png.close()

    elif cond15:
        print("Creating line graph...")

        username = args[1]

        messageData = timeData(messagesTime_data[username],1, False)
        attachmentData = timeData(attachmentsTime_data[username],1, True)

        graph_fig, graph_axes = plt.subplots(4,1)

        graph_axes[0].plot(messageData[0], messageData[1], linewidth=3, marker='o', markersize=10, color="red")
        graph_axes[0].tick_params(axis="x", which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[0].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[0].grid()
        graph_axes[0].set_title("Messages per Month", fontsize=FONT_SIZE, pad=25)

        graph_axes[1].plot(messageData[0], messageData[2], linewidth=3, marker='o', markersize=10, color="red")
        graph_axes[1].tick_params(axis="x", which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[1].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[1].grid()
        graph_axes[1].set_title("Cumulative Messages per Month", fontsize=FONT_SIZE, pad=25)

        graph_axes[2].plot(attachmentData[0], attachmentData[1], linewidth=3, marker='o', markersize=10, color="blue")
        graph_axes[2].tick_params(axis='x', which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[2].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[2].grid()
        graph_axes[2].set_title("Attachments per Month", fontsize=FONT_SIZE, pad=25)

        graph_axes[3].plot(attachmentData[0], attachmentData[2], linewidth=3, marker='o', markersize=10, color="blue")
        graph_axes[3].tick_params(axis='x', which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[3].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[3].grid()
        graph_axes[3].set_title("Cumulative Attachments per Month", fontsize=FONT_SIZE, pad=25)

        graph_fig.set_size_inches(45,30)
        plt.subplots_adjust(hspace=0.3)
        plt.suptitle(f"Messages & Attachments sent per Month in {ctx.guild.name} by {username}", fontsize=FONT_SIZE*2)

        print("Saving graph...")
        graph_fig.savefig("alltime_month_username_line.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        alltime_month_username_line_png = open("alltime_month_username_line.png", "rb")
        discord_alltime_month_username_line_png = discord.File(fp=alltime_month_username_line_png,filename="alltime_month_username_line.png")
        await ctx.send(file=discord_alltime_month_username_line_png)

        alltime_month_username_line_png.close()

    elif cond16:
        print("Creating bar graph...")

        username = args[1]

        messageData = timeData(messagesTime_data[username],1, False)
        attachmentData = timeData(attachmentsTime_data[username],1, True)

        graph_fig, graph_axes = plt.subplots(2,2)

        graph_axes[0,0].bar(messageData[0], messageData[1], color="red", width=0.5)
        graph_axes[0,0].tick_params(axis="x", which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[0,0].tick_params(axis="y", which='major', labelsize=FONT_SIZE*2)
        graph_axes[0,0].grid(axis="y")
        graph_axes[0,0].set_title("Messages per Month", fontsize=FONT_SIZE*3, pad=25)

        graph_axes[1,0].bar(messageData[0], messageData[2], color="red", width=0.5)
        graph_axes[1,0].tick_params(axis="x", which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[1,0].tick_params(axis="y", which='major', labelsize=FONT_SIZE*2)
        graph_axes[1,0].grid(axis="y")
        graph_axes[1,0].set_title("Cumulative Messages per Month", fontsize=FONT_SIZE*3, pad=25)

        graph_axes[0,1].bar(attachmentData[0], attachmentData[1], color="blue", width=0.5)
        graph_axes[0,1].tick_params(axis='x', which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[0,1].tick_params(axis="y", which='major', labelsize=FONT_SIZE*2)
        graph_axes[0,1].grid(axis="y")
        graph_axes[0,1].set_title("Attachments per Month", fontsize=FONT_SIZE*3, pad=25)

        graph_axes[1,1].bar(attachmentData[0], attachmentData[2], color="blue", width=0.5)
        graph_axes[1,1].tick_params(axis='x', which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[1,1].tick_params(axis="y", which='major', labelsize=FONT_SIZE*2)
        graph_axes[1,1].grid(axis="y")
        graph_axes[1,1].set_title("Cumulative Attachments per Month", fontsize=FONT_SIZE*3, pad=25)

        graph_fig.set_size_inches(150,50)
        plt.subplots_adjust(hspace=0.3)
        plt.suptitle(f"Messages & Attachments sent per Month in {ctx.guild.name} by {username}", fontsize=FONT_SIZE*6)

        print("Saving graph...")
        graph_fig.savefig("alltime_month_username_bar.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        alltime_month_username_bar_png = open("alltime_month_username_bar.png", "rb")
        discord_alltime_month_username_bar_png = discord.File(fp=alltime_month_username_bar_png,filename="alltime_month_username_bar.png")
        await ctx.send(file=discord_alltime_month_username_bar_png)

        alltime_month_username_bar_png.close()

    elif cond17:
        print("Creating line graph...")

        username = args[1]

        messageData = timeData(messagesTime_data[username],2, False)
        attachmentData = timeData(attachmentsTime_data[username],2, True)

        graph_fig, graph_axes = plt.subplots(4,1)

        graph_axes[0].plot(messageData[0], messageData[1], linewidth=1, marker='o', markersize=5, color="red")
        graph_axes[0].tick_params(axis="x", which='major', rotation=0, labelsize=0)
        graph_axes[0].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[0].grid()
        graph_axes[0].set_title("Messages per Day", fontsize=FONT_SIZE, pad=25)

        graph_axes[1].plot(messageData[0], messageData[2], linewidth=1, marker='o', markersize=5, color="red")
        graph_axes[1].tick_params(axis="x", which='major', rotation=0, labelsize=0)
        graph_axes[1].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[1].grid()
        graph_axes[1].set_title("Cumulative Messages per Day", fontsize=FONT_SIZE, pad=25)

        graph_axes[2].plot(attachmentData[0], attachmentData[1], linewidth=1, marker='o', markersize=5, color="blue")
        graph_axes[2].tick_params(axis='x', which='major', rotation=0, labelsize=0)
        graph_axes[2].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[2].grid()
        graph_axes[2].set_title("Attachments per Day", fontsize=FONT_SIZE, pad=25)

        graph_axes[3].plot(attachmentData[0], attachmentData[2], linewidth=1, marker='o', markersize=5, color="blue")
        graph_axes[3].tick_params(axis='x', which='major', rotation=0, labelsize=0)
        graph_axes[3].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[3].grid()
        graph_axes[3].set_title("Cumulative Attachments per Day", fontsize=FONT_SIZE, pad=25)

        graph_fig.set_size_inches(45,30)
        plt.subplots_adjust(hspace=0.3)
        plt.suptitle(f"Messages & Attachments sent per Day in {ctx.guild.name} by {username}", fontsize=FONT_SIZE*2)

        print("Saving graph...")
        graph_fig.savefig("alltime_day_username_line.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        alltime_day_username_line_png = open("alltime_day_username_line.png", "rb")
        discord_alltime_day_username_line_png = discord.File(fp=alltime_day_username_line_png,filename="alltime_day_username_line.png")
        await ctx.send(file=discord_alltime_day_username_line_png)

        alltime_day_username_line_png.close()

    elif cond18:
        print("Creating bar graph...")

        username = args[1]

        messageData = timeData(messagesTime_data[username],2, False)
        attachmentData = timeData(attachmentsTime_data[username],2, True)

        graph_fig, graph_axes = plt.subplots(2,2)

        graph_axes[0,0].bar(messageData[0], messageData[1], color="red", width=0.5)
        graph_axes[0,0].tick_params(axis="x", which='major', rotation=0, labelsize=0)
        graph_axes[0,0].tick_params(axis="y", which='major', labelsize=FONT_SIZE*2)
        graph_axes[0,0].grid(axis="y")
        graph_axes[0,0].set_title("Messages per day", fontsize=FONT_SIZE*3, pad=25)

        graph_axes[1,0].bar(messageData[0], messageData[2], color="red", width=0.5)
        graph_axes[1,0].tick_params(axis="x", which='major', rotation=0, labelsize=0)
        graph_axes[1,0].tick_params(axis="y", which='major', labelsize=FONT_SIZE*2)
        graph_axes[1,0].grid(axis="y")
        graph_axes[1,0].set_title("Cumulative Messages per Day", fontsize=FONT_SIZE*3, pad=25)

        graph_axes[0,1].bar(attachmentData[0], attachmentData[1], color="blue", width=0.5)
        graph_axes[0,1].tick_params(axis='x', which='major', rotation=0, labelsize=0)
        graph_axes[0,1].tick_params(axis="y", which='major', labelsize=FONT_SIZE*2)
        graph_axes[0,1].grid(axis="y")
        graph_axes[0,1].set_title("Attachments per Day", fontsize=FONT_SIZE*3, pad=25)

        graph_axes[1,1].bar(attachmentData[0], attachmentData[2], color="blue", width=0.5)
        graph_axes[1,1].tick_params(axis='x', which='major', rotation=0, labelsize=0)
        graph_axes[1,1].tick_params(axis="y", which='major', labelsize=FONT_SIZE*2)
        graph_axes[1,1].grid(axis="y")
        graph_axes[1,1].set_title("Cumulative Attachments per Day", fontsize=FONT_SIZE*3, pad=25)

        graph_fig.set_size_inches(150,50)
        plt.subplots_adjust(hspace=0.3)
        plt.suptitle(f"Messages & Attachments sent per Day in {ctx.guild.name} by {username}", fontsize=FONT_SIZE*6)

        print("Saving graph...")
        graph_fig.savefig("alltime_day_username_bar.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        alltime_day_username_bar_png = open("alltime_day_username_bar.png", "rb")
        discord_alltime_day_username_bar_png = discord.File(fp=alltime_day_username_bar_png,filename="alltime_day_username_bar.png")
        await ctx.send(file=discord_alltime_day_username_bar_png)

        alltime_day_username_bar_png.close()

    elif cond19:
        print("Creating line graph...")

        username = args[2]

        messageData = timeData(messagesTime_data[username],0, False)
        attachmentData = timeData(attachmentsTime_data[username],0, True)

        graph_fig, graph_axes = plt.subplots(4,1)

        graph_axes[0].plot(messageData[0], messageData[1], linewidth=3, marker='o', markersize=10, color="red")
        graph_axes[0].tick_params(axis="x", which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[0].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[0].grid()
        graph_axes[0].set_title("Messages per Year", fontsize=FONT_SIZE, pad=25)

        graph_axes[1].plot(messageData[0], messageData[2], linewidth=3, marker='o', markersize=10, color="red")
        graph_axes[1].tick_params(axis="x", which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[1].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[1].grid()
        graph_axes[1].set_title("Cumulative Messages per Year", fontsize=FONT_SIZE, pad=25)

        graph_axes[2].plot(attachmentData[0], attachmentData[1], linewidth=3, marker='o', markersize=10, color="blue")
        graph_axes[2].tick_params(axis='x', which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[2].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[2].grid()
        graph_axes[2].set_title("Attachments per Year", fontsize=FONT_SIZE, pad=25)

        graph_axes[3].plot(attachmentData[0], attachmentData[2], linewidth=3, marker='o', markersize=10, color="blue")
        graph_axes[3].tick_params(axis='x', which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[3].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[3].grid()
        graph_axes[3].set_title("Cumulative Attachments per Year", fontsize=FONT_SIZE, pad=25)

        graph_fig.set_size_inches(45,30)
        plt.subplots_adjust(hspace=0.3)
        plt.suptitle(f"Messages & Attachments sent per Year in #{args[1]} by {username}", fontsize=FONT_SIZE*2)

        print("Saving graph...")
        graph_fig.savefig("alltime_year_channel_username_line.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        alltime_year_channel_username_line_png = open("alltime_year_channel_username_line.png", "rb")
        discord_alltime_year_channel_username_line_png = discord.File(fp=alltime_year_channel_username_line_png,filename="alltime_year_channel_username_line.png")
        await ctx.send(file=discord_alltime_year_channel_username_line_png)

        alltime_year_channel_username_line_png.close()

    elif cond20:
        print("Creating bar graph...")

        username = args[2]

        messageData = timeData(messagesTime_data[username],0, False)
        attachmentData = timeData(attachmentsTime_data[username],0, True)

        graph_fig, graph_axes = plt.subplots(2,2)

        graph_axes[0,0].bar(messageData[0], messageData[1], color="red", width=0.5)
        graph_axes[0,0].tick_params(axis="x", which='major', rotation=0, labelsize=FONT_SIZE)
        graph_axes[0,0].tick_params(axis="y", which='major', labelsize=FONT_SIZE)
        graph_axes[0,0].grid(axis="y")
        graph_axes[0,0].set_title("Messages per Year", fontsize=FONT_SIZE*2, pad=25)

        graph_axes[1,0].bar(messageData[0], messageData[2], color="red", width=0.5)
        graph_axes[1,0].tick_params(axis="x", which='major', rotation=0, labelsize=FONT_SIZE)
        graph_axes[1,0].tick_params(axis="y", which='major', labelsize=FONT_SIZE)
        graph_axes[1,0].grid(axis="y")
        graph_axes[1,0].set_title("Cumulative Messages per Year", fontsize=FONT_SIZE*2, pad=25)

        graph_axes[0,1].bar(attachmentData[0], attachmentData[1], color="blue", width=0.5)
        graph_axes[0,1].tick_params(axis='x', which='major', rotation=0, labelsize=FONT_SIZE)
        graph_axes[0,1].tick_params(axis="y", which='major', labelsize=FONT_SIZE)
        graph_axes[0,1].grid(axis="y")
        graph_axes[0,1].set_title("Attachments per Year", fontsize=FONT_SIZE*2, pad=25)

        graph_axes[1,1].bar(attachmentData[0], attachmentData[2], color="blue", width=0.5)
        graph_axes[1,1].tick_params(axis='x', which='major', rotation=0, labelsize=FONT_SIZE)
        graph_axes[1,1].tick_params(axis="y", which='major', labelsize=FONT_SIZE)
        graph_axes[1,1].grid(axis="y")
        graph_axes[1,1].set_title("Cumulative Attachments per Year", fontsize=FONT_SIZE*2, pad=25)

        graph_fig.set_size_inches(100,50)
        plt.subplots_adjust(hspace=0.3)
        plt.suptitle(f"Messages & Attachments sent per Year in #{args[1]} by {username}", fontsize=FONT_SIZE*4)

        print("Saving graph...")
        graph_fig.savefig("alltime_year_channel_username_bar.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        alltime_year_channel_username_bar_png = open("alltime_year_channel_username_bar.png", "rb")
        discord_alltime_year_channel_username_bar_png = discord.File(fp=alltime_year_channel_username_bar_png,filename="alltime_year_channel_username_bar.png")
        await ctx.send(file=discord_alltime_year_channel_username_bar_png)

        alltime_year_channel_username_bar_png.close()

    elif cond21:
        print("Creating line graph...")

        username = args[2]

        messageData = timeData(messagesTime_data[username],1, False)
        attachmentData = timeData(attachmentsTime_data[username],1, True)

        graph_fig, graph_axes = plt.subplots(4,1)

        graph_axes[0].plot(messageData[0], messageData[1], linewidth=3, marker='o', markersize=10, color="red")
        graph_axes[0].tick_params(axis="x", which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[0].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[0].grid()
        graph_axes[0].set_title("Messages per Month", fontsize=FONT_SIZE, pad=25)

        graph_axes[1].plot(messageData[0], messageData[2], linewidth=3, marker='o', markersize=10, color="red")
        graph_axes[1].tick_params(axis="x", which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[1].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[1].grid()
        graph_axes[1].set_title("Cumulative Messages per Month", fontsize=FONT_SIZE, pad=25)

        graph_axes[2].plot(attachmentData[0], attachmentData[1], linewidth=3, marker='o', markersize=10, color="blue")
        graph_axes[2].tick_params(axis='x', which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[2].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[2].grid()
        graph_axes[2].set_title("Attachments per Month", fontsize=FONT_SIZE, pad=25)

        graph_axes[3].plot(attachmentData[0], attachmentData[2], linewidth=3, marker='o', markersize=10, color="blue")
        graph_axes[3].tick_params(axis='x', which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[3].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[3].grid()
        graph_axes[3].set_title("Cumulative Attachments per Month", fontsize=FONT_SIZE, pad=25)

        graph_fig.set_size_inches(45,30)
        plt.subplots_adjust(hspace=0.3)
        plt.suptitle(f"Messages & Attachments sent per Month in #{args[1]} by {username}", fontsize=FONT_SIZE*2)

        print("Saving graph...")
        graph_fig.savefig("alltime_month_channel_username_line.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        alltime_month__channel_username_line_png = open("alltime_month_channel_username_line.png", "rb")
        discord_alltime_month__channel_username_line_png = discord.File(fp=alltime_month__channel_username_line_png,filename="alltime_month_channel_username_line.png")
        await ctx.send(file=discord_alltime_month__channel_username_line_png)

        alltime_month__channel_username_line_png.close()

    elif cond22:
        print("Creating bar graph...")

        username = args[2]

        messageData = timeData(messagesTime_data[username],1, False)
        attachmentData = timeData(attachmentsTime_data[username],1, True)

        graph_fig, graph_axes = plt.subplots(2,2)

        graph_axes[0,0].bar(messageData[0], messageData[1], color="red", width=0.5)
        graph_axes[0,0].tick_params(axis="x", which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[0,0].tick_params(axis="y", which='major', labelsize=FONT_SIZE*2)
        graph_axes[0,0].grid(axis="y")
        graph_axes[0,0].set_title("Messages per Month", fontsize=FONT_SIZE*3, pad=25)

        graph_axes[1,0].bar(messageData[0], messageData[2], color="red", width=0.5)
        graph_axes[1,0].tick_params(axis="x", which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[1,0].tick_params(axis="y", which='major', labelsize=FONT_SIZE*2)
        graph_axes[1,0].grid(axis="y")
        graph_axes[1,0].set_title("Cumulative Messages per Month", fontsize=FONT_SIZE*3, pad=25)

        graph_axes[0,1].bar(attachmentData[0], attachmentData[1], color="blue", width=0.5)
        graph_axes[0,1].tick_params(axis='x', which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[0,1].tick_params(axis="y", which='major', labelsize=FONT_SIZE*2)
        graph_axes[0,1].grid(axis="y")
        graph_axes[0,1].set_title("Attachments per Month", fontsize=FONT_SIZE*3, pad=25)

        graph_axes[1,1].bar(attachmentData[0], attachmentData[2], color="blue", width=0.5)
        graph_axes[1,1].tick_params(axis='x', which='major', rotation=0, labelsize=FONT_SIZE/2)
        graph_axes[1,1].tick_params(axis="y", which='major', labelsize=FONT_SIZE*2)
        graph_axes[1,1].grid(axis="y")
        graph_axes[1,1].set_title("Cumulative Attachments per Month", fontsize=FONT_SIZE*3, pad=25)

        graph_fig.set_size_inches(150,50)
        plt.subplots_adjust(hspace=0.3)
        plt.suptitle(f"Messages & Attachments sent per Month in #{args[1]} by {username}", fontsize=FONT_SIZE*6)

        print("Saving graph...")
        graph_fig.savefig("alltime_month_channel_username_bar.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        alltime_month_channel_username_bar_png = open("alltime_month_channel_username_bar.png", "rb")
        discord_alltime_month_channel_username_bar_png = discord.File(fp=alltime_month_channel_username_bar_png,filename="alltime_month_channel_username_bar.png")
        await ctx.send(file=discord_alltime_month_channel_username_bar_png)

        alltime_month_channel_username_bar_png.close()

    elif cond23:
        print("Creating line graph...")

        username = args[2]

        messageData = timeData(messagesTime_data[username],2, False)
        attachmentData = timeData(attachmentsTime_data[username],2, True)

        graph_fig, graph_axes = plt.subplots(4,1)

        graph_axes[0].plot(messageData[0], messageData[1], linewidth=1, marker='o', markersize=5, color="red")
        graph_axes[0].tick_params(axis="x", which='major', rotation=0, labelsize=0)
        graph_axes[0].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[0].grid()
        graph_axes[0].set_title("Messages per Day", fontsize=FONT_SIZE, pad=25)

        graph_axes[1].plot(messageData[0], messageData[2], linewidth=1, marker='o', markersize=5, color="red")
        graph_axes[1].tick_params(axis="x", which='major', rotation=0, labelsize=0)
        graph_axes[1].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[1].grid()
        graph_axes[1].set_title("Cumulative Messages per Day", fontsize=FONT_SIZE, pad=25)

        graph_axes[2].plot(attachmentData[0], attachmentData[1], linewidth=1, marker='o', markersize=5, color="blue")
        graph_axes[2].tick_params(axis='x', which='major', rotation=0, labelsize=0)
        graph_axes[2].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[2].grid()
        graph_axes[2].set_title("Attachments per Day", fontsize=FONT_SIZE, pad=25)

        graph_axes[3].plot(attachmentData[0], attachmentData[2], linewidth=1, marker='o', markersize=5, color="blue")
        graph_axes[3].tick_params(axis='x', which='major', rotation=0, labelsize=0)
        graph_axes[3].tick_params(axis="y", which='major', labelsize=FONT_SIZE/1.5)
        graph_axes[3].grid()
        graph_axes[3].set_title("Cumulative Attachments per Day", fontsize=FONT_SIZE, pad=25)

        graph_fig.set_size_inches(45,30)
        plt.subplots_adjust(hspace=0.3)
        plt.suptitle(f"Messages & Attachments sent per Day in #{args[1]} by {username}", fontsize=FONT_SIZE*2)

        print("Saving graph...")
        graph_fig.savefig("alltime_day_channel_username_line.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        alltime_day_channel_username_line_png = open("alltime_day_channel_username_line.png", "rb")
        discord_alltime_day_channel_username_line_png = discord.File(fp=alltime_day_channel_username_line_png,filename="alltime_day_channel_username_line.png")
        await ctx.send(file=discord_alltime_day_channel_username_line_png)

        alltime_day_channel_username_line_png.close()

    elif cond24:
        print("Creating bar graph...")

        username = args[2]

        messageData = timeData(messagesTime_data[username],2, False)
        attachmentData = timeData(attachmentsTime_data[username],2, True)

        graph_fig, graph_axes = plt.subplots(2,2)

        graph_axes[0,0].bar(messageData[0], messageData[1], color="red", width=0.5)
        graph_axes[0,0].tick_params(axis="x", which='major', rotation=0, labelsize=0)
        graph_axes[0,0].tick_params(axis="y", which='major', labelsize=FONT_SIZE*2)
        graph_axes[0,0].grid(axis="y")
        graph_axes[0,0].set_title("Messages per day", fontsize=FONT_SIZE*3, pad=25)

        graph_axes[1,0].bar(messageData[0], messageData[2], color="red", width=0.5)
        graph_axes[1,0].tick_params(axis="x", which='major', rotation=0, labelsize=0)
        graph_axes[1,0].tick_params(axis="y", which='major', labelsize=FONT_SIZE*2)
        graph_axes[1,0].grid(axis="y")
        graph_axes[1,0].set_title("Cumulative Messages per Day", fontsize=FONT_SIZE*3, pad=25)

        graph_axes[0,1].bar(attachmentData[0], attachmentData[1], color="blue", width=0.5)
        graph_axes[0,1].tick_params(axis='x', which='major', rotation=0, labelsize=0)
        graph_axes[0,1].tick_params(axis="y", which='major', labelsize=FONT_SIZE*2)
        graph_axes[0,1].grid(axis="y")
        graph_axes[0,1].set_title("Attachments per Day", fontsize=FONT_SIZE*3, pad=25)

        graph_axes[1,1].bar(attachmentData[0], attachmentData[2], color="blue", width=0.5)
        graph_axes[1,1].tick_params(axis='x', which='major', rotation=0, labelsize=0)
        graph_axes[1,1].tick_params(axis="y", which='major', labelsize=FONT_SIZE*2)
        graph_axes[1,1].grid(axis="y")
        graph_axes[1,1].set_title("Cumulative Attachments per Day", fontsize=FONT_SIZE*3, pad=25)

        graph_fig.set_size_inches(150,50)
        plt.subplots_adjust(hspace=0.3)
        plt.suptitle(f"Messages & Attachments sent per Day in #{args[1]} by {username}", fontsize=FONT_SIZE*6)

        print("Saving graph...")
        graph_fig.savefig("alltime_day_channel_username_bar.png", bbox_inches='tight', pad_inches=1.0)
        plt.close()

        print("Printing graph...")
        alltime_day_channel_username_bar_png = open("alltime_day_channel_username_bar.png", "rb")
        discord_alltime_day_channel_username_bar_png = discord.File(fp=alltime_day_channel_username_bar_png,filename="alltime_day_channel_username_bar.png")
        await ctx.send(file=discord_alltime_day_channel_username_bar_png)

        alltime_day_channel_username_bar_png.close()

    os.chdir(WORKING_DIRECTORY)

    print(f"Current working directory:\n{os.getcwd()}")

#Random command-----------------------------------------------------------------
@client.command()
async def random(ctx):
    print("RANDOM---------------------------------------------------------------")

    serverthere = checkServer(ctx.guild)

    if serverthere != False:
        print("ERROR: Server database does not exist")
        os.chdir(WORKING_DIRECTORY)
        return

    args = getargs(ctx.message.clean_content)

    guild_info = getServer(ctx.guild)
    guild_fields = guild_info.split(">")
    channel_fields = guild_fields[2]

    if len(args) >= 2 and args[1] in channel_fields:

        channel_id = getChannelID(args[1], channel_fields)

        navigatedir(ctx.guild.id,channel_id)

        messages_data = pd.read_csv(f"{channel_id} strippedMessages.csv", dtype="str")
        attachments_data = pd.read_csv(f"{channel_id} strippedAttachments.csv", dtype="str")

    else:

        navigatedir(ctx.guild.id)

        messages_data = pd.read_csv(f"{ctx.guild.id} strippedMessages.csv", dtype="str")
        attachments_data = pd.read_csv(f"{ctx.guild.id} strippedAttachments.csv", dtype="str")

    cond1 = (len(args) == 2 and args[1].lower() == "message")
    cond2 = (len(args) == 2 and args[1].lower() == "attachment")

    cond3 = (len(args) == 3 and args[1] in messages_data.columns and args[2].lower == "message")
    cond4 = (len(args) == 3 and args[1] in attachments_data.columns and args[2].lower == "attachment")

    cond5 = (len(args) == 3 and args[1] in channel_fields and args[2].lower() == "message")
    cond6 = (len(args) == 3 and args[1] in channel_fields and args[2].lower() == "attachment")

    cond7 = (len(args) == 4 and args[1] in channel_fields and args[2] in messages_data.columns and args[3].lower() == "message")
    cond8 = (len(args) == 4 and args[1] in channel_fields and args[2] in attachments_data.columns and args[3].lower() == "attachment")

    arg_validation = (cond1 or cond2 or cond3 or cond4 or cond5 or cond6 or cond7 or cond8)

    if arg_validation == False:
        print("ERROR: Invalid args")
        os.chdir(WORKING_DIRECTORY)
        return

    if cond1:

        while True:
            username_choice = rdm.choice(messages_data.columns)
            data = messages_data[username_choice].dropna()
            if len(data) > 0:
                break

        random_message = str(data.sample(n=1).values[0])
        tags = random_message.split(" ", 1)
        timestamp = tags[0].split("|")
        message = tags[1]

        output_str = f"This was sent on **{timestamp[0]}** at **{timestamp[1]}** by **{username_choice}**\n\n{message}"
        await ctx.send(output_str)

    elif cond2:

        while True:
            username_choice = rdm.choice(messages_data.columns)
            data = attachments_data[username_choice].dropna()
            data = data[data.str.contains("NULL") == False]
            if len(data) > 0:
                break

        random_message = str(data.sample(n=1).values[0])
        tags = random_message.split(" ", 1)
        timestamp = tags[0].split("|")
        attachment = tags[1]

        output_str = f"This was sent on **{timestamp[0]}** at **{timestamp[1]}** by **{username_choice}**\n\n{attachment}"
        await ctx.send(output_str)

    elif cond3:

        username_choice = args[1]
        data = messages_data[username_choice].dropna()
        if len(data) == 0:
            output_str = f"**{username_choice}** has no messages to choose from throughout the server"
            await ctx.send(output_str)
            return

        random_message = str(data.sample(n=1).values[0])
        tags = random_message.split(" ", 1)
        timestamp = tags[0].split("|")
        message = tags[1]

        output_str = f"This was sent on **{timestamp[0]}** at **{timestamp[1]}** by **{username_choice}**\n\n{message}"
        await ctx.send(output_str)

    elif cond4:

        username_choice = args[1]
        data = attachments_data[username_choice].dropna()
        data = data[data.str.contains("NULL") == False]
        if len(data) == 0:
            output_str = f"**{username_choice}** has no attachments to choose from throughout the server"
            await ctx.send(output_str)
            return

        random_message = str(data.sample(n=1).values[0])
        tags = random_message.split(" ", 1)
        timestamp = tags[0].split("|")
        attachment = tags[1]

        output_str = f"This was sent on **{timestamp[0]}** at **{timestamp[1]}** by **{username_choice}**\n\n{attachment}"
        await ctx.send(output_str)

    elif cond5:

        while True:
            username_choice = rdm.choice(messages_data.columns)
            data = messages_data[username_choice].dropna()
            if len(data) > 0:
                break
            elif username_choice not in tried_usernames:
                tried_usernames.append(username_choice)

            if len(username_choice) == len(messages_data.columns):
                output_str = f"ERROR: #{args[1]} has no messages"
                await ctx.send(output_str)
                return

        random_message = str(data.sample(n=1).values[0])
        tags = random_message.split(" ", 1)
        timestamp = tags[0].split("|")
        message = tags[1]

        output_str = f"This was sent on **{timestamp[0]}** at **{timestamp[1]}** by **{username_choice}** in **#{args[1]}**\n\n{message}"
        await ctx.send(output_str)


    elif cond6:

        tried_usernames = []

        while True:
            username_choice = rdm.choice(attachments_data.columns)
            data = attachments_data[username_choice].dropna()
            data = data[data.str.contains("NULL") == False]
            if len(data) > 0:
                break
            elif username_choice not in tried_usernames:
                tried_usernames.append(username_choice)

            if len(tried_usernames) == len(attachments_data.columns):
                output_str = f"ERROR: #{args[1]} has no attachments to choose from"
                await ctx.send(output_str)
                return

        random_message = str(data.sample(n=1).values[0])
        tags = random_message.split(" ", 1)
        timestamp = tags[0].split("|")
        attachment = tags[1]

        output_str = f"This was sent on **{timestamp[0]}** at **{timestamp[1]}** by **{username_choice}** in **#{args[1]}**\n\n{attachment}"
        await ctx.send(output_str)

    elif cond7:

        username_choice = args[2]
        data = messages_data[username_choice].dropna()
        if len(data) == 0:
            output_str = f"**{username_choice}** has no messages to choose from in #{args[1]}"
            await ctx.send(output_str)
            return

        random_message = str(data.sample(n=1).values[0])
        tags = random_message.split(" ", 1)
        timestamp = tags[0].split("|")
        message = tags[1]

        output_str = f"This was sent on **{timestamp[0]}** at **{timestamp[1]}** by **{username_choice}** in **#{args[1]}**\n\n{message}"
        await ctx.send(output_str)

    elif cond8:

        username_choice = args[2]
        data = attachments_data[username_choice].dropna()
        data = data[data.str.contains("NULL") == False]
        if len(data) == 0:
            output_str = f"**{username_choice}** has no attachments to choose from in #{args[1]}"
            await ctx.send(output_str)
            return

        random_message = str(data.sample(n=1).values[0])
        tags = random_message.split(" ", 1)
        timestamp = tags[0].split("|")
        attachment = tags[1]

        output_str = f"This was sent on **{timestamp[0]}** at **{timestamp[1]}** by **{username_choice}** in **#{args[1]}**\n\n{attachment}"
        await ctx.send(output_str)


    os.chdir(WORKING_DIRECTORY)

    print(f"Current working directory:\n{os.getcwd()}")

client.run(TOKEN)
