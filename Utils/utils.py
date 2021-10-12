import discord, datetime, pymongo, os, datetime, re, requests
from discord.ext import commands, tasks
from discord.ext.commands.errors import MissingRequiredArgument
from colorama import Fore

# Connection To Database (MongoDB)
mongoClient = pymongo.MongoClient(os.environ.get('BOT_DB'))
db = mongoClient.get_database("refuge").get_collection("server-data")
db2 = mongoClient['refuge']
antitoggle = db2['antitoggle']
blacklist = db2['blacklist']
limits = db2['limits']
punishment = db2['punishments']

class utils:

    @classmethod
    async def create_guild(self, guild : discord.Guild):
        dp = os.environ.get('default_punishment')
        db.insert_one({
            #Whitelist
            "whitelisted_users": [guild.owner_id],
            "whitelisted_roles": [],
            "whitelist-link-channels": [],
            "auto-roles": [],
            
            #Guild Data
            "prefix": f"{os.environ.get('default_prefix')}",
            "guild_id": guild.id,
            "guild_name": guild.name,
            "vanity_url": None if guild.premium_tier == 3 else None,
            
            #Toggles
            "anti-nuke": True,
            "anti-ban": True,
            "anti-kick": True,
            "anti-channel-create": True,
            "anti-channel-delete": True,
            "anti-role-create": True,
            "anti-role-delete": True,
            "anti-bot": True,
            "logging": True,

            #Limits
            "anti-ban-limit": 1,
            "anti-unban-limit": 1,
            "anti-kick-limit": 1, 
            "anti-channel-create-limit": 1,
            "anti-channel-delete-limit": 1,
            "anti-role-create-limit": 1,
            "anti-role-delete-limit": 1,
            "anti-webhook-create-limit": 1,
            "anti-webhook-delete-limit": 1,
            "anti-widget-create-limit": 1,
            "anti-widget-delete-limit": 1,
            "anti-integration-create-limit": 1,
            "anti-integration-delete-limit": 1,
            "anti-emoji-create-limit": 1,
            "anti-emoji-delete-limit": 1,
            "anti-permissions-limit" : "manage_roles",
            "anti-spam-limit": 10,
            
            #Logging
            "log-channel": None,
            "welcome-channel": None,
            "boost-channel": None,
            "leave-channel": None,
            "boost-message": None,
            "welcome-message": None,
            "leave-message": None,
            "boost-message": None,
            "welcome-embed": False,
            "boost-embed": False,
            "leave-embed": False,

            #Punishments
            "anti-ban-punishment": f'{dp}',
            "anti-kick-punishment": f'{dp}', 
            "anti-prune-punishment": f'{dp}',
            "anti-channel-create-punishment": f'{dp}',
            "anti-channel-delete-punishment": f'{dp}',
            "anti-role-create-punishment": f'{dp}',
            "anti-role-delete-punishment": f'{dp}',
            "anti-webhook-create-punishment": f'{dp}',
            "anti-webhook-delete-punishment": f'{dp}',
            "anti-widget-create-punishment": f'{dp}',
            "anti-widget-delete-punishment": f'{dp}',
            "anti-integration-create-punishment": f'{dp}',
            "anti-integration-delete-punishment": f'{dp}',
            "anti-emoji-create-punishment": f'{dp}',
            "anti-emoji-delete-punishment": f'{dp}',
            "anti-permissions-punishment": f'{dp}',
            "anti-vanity-punishment": f'{dp}',
            "anti-bot-punishment": f'{dp}',
            "anti-spam-punishment": 'mute',
            "anti-link-punishment": 'mute'

        })

    """A simple utility class for all functions that will be used in the bot."""
    
    @classmethod
    def create_embed(self, text):
        embed = discord.Embed(
            description=text,
            colour=0x2f3136,
        )
        return embed

    @classmethod
    def msg_contains_word(self, msg, word):
        return re.search(fr'\b({word})\b', msg) is not None 

    @classmethod
    def clear(self, guild: discord.Guild, value: str):
        data = self.find_data(guild, value)
        try:
            for index in data:
                if index != guild.owner_id:
                    db.update_one({"guild_id": guild.id}, {"$pull": {value: index}})
                else:
                    pass
        except:
            raise KeyError
    

    @classmethod
    def is_whitelisted(self, member: discord.Member):
        """Checks to see if a user is whitelisted."""
        if member.id in db.find_one({"guild_id": member.guild.id})["whitelisted"]:
            return True
        else:
            return False
    
    @classmethod
    def format_antilogs(self, dm: False, user, guild: None, actionon: None, action, rms):
        if dm == False:
            embed = discord.Embed(title="<a:r_raid:867577983933218827> Stopped Raid Attempt.", color=0x2f3136, timestamp=datetime.datetime.utcnow())
            if user.bot:
                embed.add_field(name="<:r_member:866864263116750878> Raider (bot)", value=f"`{user}` (bot)", inline=False)
            else:
                embed.add_field(name="<:r_member:866864263116750878> Raider", value=f"`{user}`", inline=False)
            if actionon == user or actionon == type(user):
                embed.add_field(name="<:users_logo:776597644410748938> Caught In Raid", value=f"`{actionon}`")
            elif actionon == "channel-":
                embed.add_field(name="<:Icon_TextChannel:776616614224855040> Channel Deleted", value=f"`{actionon}`")
            elif actionon == "channel+":
                embed.add_field(name="<:Icon_TextChannel:776616614224855040> Channel Created", value=f"`{actionon}`")
            elif actionon == "role-":
                embed.add_field(name="<:r_role:860643526093438986> Role Deleted", value=f"`{actionon}`")
            elif actionon == "role+":
                embed.add_field(name="<:r_role:860643526093438986> Role Created", value=f"`{actionon}`")
            elif actionon == "permissions":
                embed.add_field(name="<:r_role:860643526093438986> Role Updated", value=f"`{actionon}`") 
            elif actionon == "vanity":
                embed.add_field(name="📃 Vanity Changed", value=f"`{actionon}`")
            else:
                embed.add_field(name="❔ Unkown Trigger", value=f"`{actionon}`")
            embed.add_field(name="<:r_hammer:860614861238960148> Action Taken", value=f"`{action}`", inline=False)
            embed.add_field(name="<a:r_timer:866863301447516180> Response Time", value=f"`{rms}` seconds")
            return embed
        if dm == True:
            embed = discord.Embed(
                title="__refuge's antinuke has been triggered!__", 
                description=f"**raider =>** {user}\n**server =>** {guild.name}\n**action =>** {actionon}\n**action taken =>** {action}"
            )
            embed.set_footer(text="Warning: THIS IS BETA FEATURE!")
            return embed

    @classmethod
    def format_modlogs(self, user, reason, action, moderator, unaction, channel, time, guild):
        embed = discord.Embed(title="Moderation Logs", color=0x2f3136, timestamp=datetime.datetime.utcnow())
        embed.add_field(name="<:Moderator:863478053800116304> Moderator:", value=f"{moderator}", inline=False)
        embed.add_field(name="<:Rules:863478096366927872> Reason:", value=f"{reason}", inline=False)
        embed.add_field(name="<:Settings:852618812657762314> Details", value=f"<:Arrow:863478107578695700> Channel: {channel}\n<:Arrow:863478107578695700> Time: `{time}`\n<:Arrow:863478107578695700> Guild: `{guild}`", inline=False)
        embed.add_field(name="<:OnlineDot:861990296217059359> Successful Actions:", value=f"`{action}`", inline=False)
        embed.add_field(name="<:OfflineDot:861990530417164328> Unsuccessful Actions:", value=f"`{unaction}`", inline=False)
        return embed

    @classmethod
    def is_admin(self, member: discord.Member or discord.User, guild: discord.Guild = None):
        """Checks to see if a user is an admin."""
        if member is discord.Member or guild is None:
            if member.id in db.find_one({"guild_id": member.guild.id})["admins"] or member.guild_permissions.administrator:
                return True
            else:
                return False
        if member is discord.User:
            if member.id in db.find_one({"guild_id": guild.id})["admins"]:
                return True
            else:
                return False 
        
    
    @classmethod
    def is_owner(self, member: discord.User or discord.Member, guild: discord.Guild=None):
        """Checks to see if a user is an owner."""
        if member is discord.Member or guild is None:
            if member.id in db.find_one({"guild_id": member.guild.id})["owners"]:
                return True
            else:
                return False

        if member is discord.User:
            if member.id in db.find_one({"guild_id": guild.id})["owners"]:
                return True
            else:
                return False
           

    @classmethod
    def is_guild_owner(self, guild: discord.Guild, user: discord.Member):
        """Checks to see if a user is the guild owner."""
        if user.id == guild.owner_id:
            return True
        else:
            return False

    @classmethod
    async def mute(self, guild: discord.Guild, member: discord.Member, reason=None):
        muted = discord.utils.get(guild.roles, name="Muted")
        if not muted:
            muted = await guild.create_role(name="Muted")
            for channel in guild.channels:
                await channel.set_permissions(muted, speak=False, send_messages=False, read_message_history=True, read_messages=True, connect=False)
        if reason == None:
            reason = f"{self.bot.user.name} | Mute"

        else:
            if muted in member.roles:
                return 
            else: 
                if len(member.roles) == 0:
                    pass
                else:
                    try:
                        for role in member.roles:
                            await member.remove_roles(role, reason=reason)
                    except:
                        pass
                
                await member.add_roles(muted, reason=reason)


    @classmethod
    def has_logging(self, guild: discord.Guild):
        if bool(db.find_one({"guild_id": guild.id})["logging"]) is True and db.find_one({"guild_id": guild.id})["logs_channel"] is not None:
            return True
        else:
            return False

    @classmethod
    def set_data(self, typeKey: str, guild: discord.Guild, index: str, value):
        """Sets the data in a database."""
        db.update_one({"guild_id": guild.id}, {typeKey: {index: value}})

    @classmethod
    def find_data(self, guild: discord.Guild, value: str = None):
        """Finds specific data in a database."""
        if value is not None:
            return db.find_one({"guild_id": guild.id})[value]
        else:
            return db.find_one({"guild_id": guild.id})

    @classmethod
    def contains(self, object: discord.Role or discord.User or discord.TextChannel, guild: discord.Guild, value: str):
        if object.id in db.find_one({"guild_id": guild.id})[value]:
            return True
        else:
            return False
    
    @classmethod
    def set_toggle(self, typeKey: str, guild: discord.Guild, index: str, value: bool):
        """Sets the toggle in a database."""
        db.update_one({"guild_id": guild.id}, {typeKey: {index: value}})

    @classmethod
    def upsert_data(self, guild: discord.Guild, index: str, id):
        db.update_one({"guild_id": guild.id}, {"$push": {index: id }})
    
    @classmethod
    def pull_data(self, guild: discord.Guild, index: str, id):
        db.update_one({"guild_id": guild.id}, {"$pull": {index: id }})

    @classmethod
    def delete_guild(self, guild: discord.Guild):
        """Deletes the guild from selected database."""
        db.delete_one({"guild_id": guild.id})

    @classmethod
    def make_request(self, type: str, url, headers=None, json=None):
        """Sends a get request."""
        if type == "GET" or "get":
            if headers is None or json is None:
                return requests.get(url)
            else:
                return requests.get(url, headers={'Authorization': f"Bot + {headers}"}, json=json)
        
        elif type == "POST" or "post":
            if headers is None or json is None:
                requests.post(url)
            else:
                requests.post(url, header={'Authorization': f"Bot + {headers}"}, json=json)

        elif type == "Put" or "put":
            if headers is None or json is None:
                requests.put(url)
            else:
                requests.put(url, header={'Authorization': f"Bot + {headers}"}, json=json)
        else:
            raise MissingRequiredArgument or AttributeError

    @classmethod
    def get_response(self, type: str, url, headers=None, json=None):
        """Sends a get request with the response."""
        if type == "GET" or "get":
            if headers is None or json is None:
                return requests.get(url).json()
            else:
                return requests.get(url, headers={'Authorization': f"Bot + {headers}"}, json=json).json()
        else:
            raise MissingRequiredArgument or AttributeError

    @classmethod
    def setup(self, bot: commands.AutoShardedBot):
        """Loads all bot cogs."""
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') or '__pycache__' not in filename:
                bot.load_extension(f'cogs.{filename[:-3]}')
            else:
                print(f'Unable to load {filename[:-3]}')

    @classmethod
    async def get_prefix(self, bot, message):
        """Gets the bot prefix."""
        if message.guild:
            try:
                prefix = db.find_one({"guild_id": message.guild.id})["prefix"]
                return commands.when_mentioned_or(prefix,)(bot, message)
            except(KeyError, AttributeError, TypeError):
                return commands.when_mentioned_or('.')(bot, message)
        else:
            return commands.when_mentioned_or('.')(bot, message)

    @classmethod
    async def status_task(self, bot: commands.AutoShardedBot):
        """A simple status task loop."""
        while True:
            count = 0 
            for g in bot.guilds:
                count += len(g.members) 

            activity3 = discord.Game(name=".help")

            await bot.change_presence(status=discord.Status.online, activity=activity3)