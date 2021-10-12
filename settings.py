import discord, os, random

os.environ['BOT_TOKEN']='ODU5MTUyOTcyOTM5MTMyOTI4.YNoijw.dMz3luazZ0qFnZ-QdaMpl_ZLzkg' # test bot token
#os.environ['BOT_TOKEN']='' # main bot token 
os.environ['BOT_DB']='mongodb+srv://venue:saiv@botsdb.ihs3a.mongodb.net/refuge?retryWrites=true&w=majority'
os.environ['BOT_VERSION']='-1.4.5'
os.environ['ONLINE_CHANNEL_ID']='849351260493709354'
os.environ['default_prefix']='%'
os.environ['default_punishment']='ban'


# EMBED HELPERS

def not_server_owner_msg():
    embed = discord.Embed(
        description="<:r_no:847976222793269250> This command can only be used by the `server owner`.",
        colour=0xE30000,
    )
    return embed


def create_embed(text):
    embed = discord.Embed(
        description=text,
        colour=int(''.join([random.choice('0123456789ABCDEF') for x in range(6)]), 16),
    )
    return embed

def create_invis_embed(text):
    embed = discord.Embed(
        description=text,
        colour=0x2F3136,
    )
    return embed

def create_error_embed(text):
    embed = discord.Embed(
        description=f"<:r_no:847976222793269250> {text}",
        colour=0xE30000,
    )
    return embed