import discord
import requests
import sqlite3

db = sqlite3.connect('id.db')
client = discord.Client()


def create_table():
    #db = sqlite3.connect('id.db')
    db.execute('''CREATE TABLE ID
                 (SERVER            INT      NOT NULL,
                 CHANNEL           INT      NOT NULL,
                 ROLE               TEXT    NOT NULL    DEFAULT "DerBotManager");''')
    #db.close()

def append_table(server_id, channel_id):
    #db = sqlite3.connect('id.db')
    db.execute(f"INSERT INTO ID (SERVER, CHANNEL) VALUES ({server_id}, {channel_id})")
    db.commit()
    #db.close()

def delete_value(server_id):
    #db = sqlite3.connect('id.db')
    db.execute(f"DELETE from ID where server like {server_id}")
    db.commit()
    #db.close()

def update_value(server_id, channel_id):
    db.execute(f"UPDATE ID set CHANNEL = {channel_id} where SERVER like {server_id}")
    db.commit()

def search_table(value):
    #db = sqlite3.connect('id.db')
    cursor = db.execute(f"SELECT SERVER, CHANNEL from ID where SERVER like {value}")
    for data in cursor:
        if value == data[0]:
            #db.close()
            return data[1]

def change_role(role):
    db.execute(f"UPDATE ID set ROLE = '{role}'")
    db.commit()

def search_role(role):
    cursor = db.execute(f"SELECT ROLE from ID where ROLE like '{role}'")
    for data in cursor:
        if role == data[0]:
            #db.close()
            return data[1]

def check_table():
    table = db.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='ID'; """).fetchall()
    if table == []:  #if table does not exist, create new one
        create_table()


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
        for role in roles:
            if role.name == "DerBotManager":
                has_permission = True
                break
            else:
                has_permission = False

    if message.content.startswith("$help"):
        embed=discord.Embed(color=0x00daff)
        embed.set_thumbnail(url="https://raw.githubusercontent.com/l0l67/ServerConnector/main/pepega.jpg")
        embed.add_field(name="$help", value="show this message", inline=False)
        embed.add_field(name="$set-channel", value="Set the channel where messages will be send", inline=True)
        embed.add_field(name="$delete-config", value="Stop the bot from sending messages", inline=True)
        embed.add_field(name="$set-role", value="Change the role required to use the bot commands", inline=True)
        embed.set_footer(text="https://github.com/l0l67/ServerConnector")
        await message.channel.send(embed=embed)

    if message.content.startswith('$set-role') and message.author.top_role.permissions.administrator:
        new_role = message.content.split(' ')[1]
        if search_role(new_role) == None:
            print("added new")
            change_role(new_role)
        else:
            print("already there")


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



    if message.content.startswith('$') == False:
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
