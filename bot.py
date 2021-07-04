import discord
import requests
import sqlite3

db = sqlite3.connect('id.db')
client = discord.Client()


def create_table():
    db.execute('''CREATE TABLE ID
                 (SERVER            INT      NOT NULL,
                 CHANNEL           INT      NOT NULL,
                 LCHANNEL           INT    NOT NULL     DEFAULT 0,
                 ROLE               TEXT    NOT NULL    DEFAULT "DerBotManager");''')

def append_table(server_id, channel_id):
    db.execute(f"INSERT INTO ID (SERVER, CHANNEL) VALUES ({server_id}, {channel_id})")
    db.commit()

def delete_value(server_id):
    db.execute(f"DELETE from ID where server like {server_id}")
    db.commit()

def update_value(server_id, channel_id):
    db.execute(f"UPDATE ID set CHANNEL = {channel_id} where SERVER like {server_id}")
    db.commit()

def search_table(value):
    cursor = db.execute(f"SELECT SERVER, CHANNEL from ID where SERVER like {value}")
    for data in cursor:
        if value == data[0]:
            return data[1]

def change_role(server, role):
    db.execute(f"UPDATE ID set ROLE = '{role}' where SERVER like {server}")
    db.commit()

def search_role(server, role):
    cursor = db.execute(f"SELECT SERVER, ROLE from ID where ROLE like '{role}' AND SERVER like {server}")
    for data in cursor:
        if str(role) == str(data[1]):
            return data[1]


#can be implemented in search_table and update_value
def change_reciever(server, channel):
    db.execute(f"UPDATE ID set LCHANNEL = {channel} where SERVER like {server}")
    db.commit()

def search_reciever(server, channel):
    cursor = db.execute(f"SELECT SERVER, LCHANNEL from ID where LCHANNEL like {channel} AND SERVER like {server}")
    for data in cursor:
        if str(channel) == str(data[1]):
            return data[1]


def check_table():
    table = db.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='ID'; """).fetchall()
    if table == []:  #if table does not exist, create new one
        create_table()
        append_table(0, 0)

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="$help"))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$"): #check if user has a specific role
        roles = message.author.roles
        server = message.guild.id

        print("---------------------------------------------------")
        print(f"{message.author} from {server} : {message.content}")

        for role in roles:
            if role.name == search_role(server, role) or role.permissions.administrator:
                has_permission = True
                break
            else:
                has_permission = False

    if message.content.startswith("$help"):
        embed=discord.Embed(color=0x00daff)
        embed.set_thumbnail(url="https://raw.githubusercontent.com/l0l67/ServerConnector/main/pepega.jpg")
        embed.add_field(name="$help", value="show this message", inline=False)
        embed.add_field(name="$set-channel", value="Set the channel where messages will be send", inline=False)
        embed.add_field(name="$set-listen-channel", value="Set the channel where the bot listens for messages", inline=False)
        embed.add_field(name="$delete-config", value="Stop the bot from sending messages", inline=False)
        embed.add_field(name="$set-role", value="Change the role required to use the bot commands", inline=False)
        embed.set_footer(text="https://github.com/l0l67/ServerConnector")
        await message.channel.send(embed=embed)

    if message.content.startswith('$set-role') and has_permission:
        new_role = message.content.split(' ')[1]
        server = message.guild.id
        if search_table(server) == None:
            append_table(server, int(message.channel.id))
        if search_role(server, new_role) == None:
            await message.channel.send(f"New role is {new_role}")
            change_role(server, new_role)
        else:
            await message.channel.send(f"Already set to {new_role}")


    if message.content.startswith('$set-channel') and has_permission == True:
        channel = message.content.split(' ')[1]
        init_channel = channel
        server = message.guild.id

        if discord.utils.find(lambda m: m.name == channel, message.guild.text_channels) != None: #only accepts string channel names not ids
            if channel.isdigit() == False:  #double check if channel is a string
                channel = discord.utils.get(message.guild.text_channels, name=channel)
                channel = channel.id
            if search_table(server) == None:    #if server has no entry in db add a new one
                append_table(server, int(channel))
            else:
                update_value(server, int(channel))
            await message.channel.send(f"Messages will now be send to channel {init_channel}")
        else:
            await message.channel.send(f"Channel {init_channel} not found")

    if message.content.startswith('$delete-config') and has_permission == True:
        server = message.guild.id

        if search_table(server) == None:
            await message.channel.send(f"Nothing to delete...")
        else:
            delete_value(server)
            await message.channel.send(f"Deleted config for this Server, messages will not be send anymore")

    if message.content.startswith('$set-listen-channel'):
        channel = message.content.split(' ')[1]
        init_channel = channel
        server = message.guild.id
        if discord.utils.find(lambda m: m.name == channel, message.guild.text_channels) != None: #only accepts string channel names not ids
            if channel.isdigit() == False:  #double check if channel is a string
                channel = discord.utils.get(message.guild.text_channels, name=channel)
                channel = channel.id
            if search_reciever(server, channel) == None:
                change_reciever(server, channel)
                await message.channel.send(f"{channel} is now the listening channel")
            else:
                await message.channel.send(f"{channel} is already set")

    if message.content.startswith('$') == False and search_reciever(message.guild.id, message.channel.id) != None:
        msg_author = message.author
        msg_content = message.content
        msg_origin = message.guild

        if len(message.attachments) > 0:
            msg_attachment_url = message.attachments[0].url
            attachment = True
        else:
            attachment = False

        for guild in client.guilds: #send messages to every configured server
            if guild != message.guild:  #dont send messages to origin server

                if search_table(guild.id) != None:  #only proceed if the server has a channel set
                    text_channel_position = client.get_channel(search_table(guild.id)).position

                    if attachment == False:
                        await guild.text_channels[text_channel_position].send(f"{msg_author} from {msg_origin}: {msg_content}")
                    else:
                        await guild.text_channels[text_channel_position].send(f"{msg_author} from {msg_origin}: {msg_attachment_url}")



check_table()
client.run('Bot-token')
