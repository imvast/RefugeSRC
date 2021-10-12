# Imports
import discord, os, pymongo, math, time, random, asyncio
from colorama import Fore as C
from settings import *
from discord.ext import commands

# Connect to MongoDB
mongoClient = pymongo.MongoClient(os.environ.get('BOT_DB'))
db = mongoClient.get_database("refuge").get_collection("server-data")
db2 = mongoClient['refuge']
antitoggle = db2['antitoggle']
blacklist = db2['blacklist']
gprefix = db['prefix']
limits = db2['limits']

def blacklist_check():
    def predicate(ctx):
        author_id = ctx.author.id
        if blacklist.find_one({'user_id': author_id}):
            return False
        return True
    return commands.check(predicate)


class Config(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.db = db
        self.colour = discord.Colour.random()
        print(f"{C.CYAN}[Status] Cog Loaded: Config" + C.RESET)


def setup(client):
    client.add_cog(Config(client))