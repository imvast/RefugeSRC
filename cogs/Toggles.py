# Imports
import discord, pymongo, os
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
    

class Toggles(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.db = db
        self.colour = discord.Colour.random()
        print(f"{C.CYAN}[Status] Cog Loaded: Toggles" + C.RESET)
    

    @commands.group(
      name="toggle",
      description="toggle each module",
      usage="toggle <module> <on/off>",
      aliases=["toggles"],
      invoke_without_command=True,
      case_insensitive=True
    )
    @commands.cooldown(1, 2, commands.BucketType.channel)
    @blacklist_check()
    async def toggle(self, ctx):
      if ctx.message.author.id == ctx.guild.owner.id:
        embed = discord.Embed(
          title="Setting Anti-Nuke Toggles (`BETA`)", 
          description="\nGetting started with toggles. First off, the command for enabling or disabling a module of the anti-nuke can be reached by doing: `%toggle ?set <module> <type>`",
          colour=0x2F3136
        )
        embed.add_field(
          name="Types",
          value="A list of current changeable anti-nuke modules to toggle. Make sure to use the exact word and spelling when changing for there to be no issues.\nUsage: `%toggle ?types`"
        )
        embed.add_field(
          name="Set",
          value="Sets the toggle of the chosen anti feature.\nUsage: `%toggle ?set <module> <setting>`\nExample: `%toggle ?set bans true`\nExample 2: `%toggle ?set bans false`"
        )
        await ctx.send(embed=embed)
      else:
        await ctx.send(embed=not_server_owner_msg())


    @toggle.command(
      name="?types",
      invoke_without_command=True
    )
    @blacklist_check()
    async def toggle_types(self, ctx):
      if ctx.message.author.id == ctx.guild.owner.id:
        embed = discord.Embed(
          title="Toggle Types", 
          description=" **Usage** <:r_empty:863922473362522134> <:r_empty:863922473362522134><:r_empty:863922473362522134> **Type**```\n・ Bans    | anti-ban\n・ Kicks   | anti-kick\n・ Chan+   | anti-channel-create\n・ Chan-   | anti-channel-delete\n・ Role+   | anti-role-create\n・ Role-   | anti-role-delete\n・ Webhook | anti-webhook\n・ Vanity  | anti-vanity-steal\n・         | anti-alts```", 
          colour=self.colour
        )
        await ctx.send(embed=embed)
      else:
        await ctx.reply(embed=not_server_owner_msg(), delete_after=15)


    @toggle.group(
      name="?set",
      invoke_without_command=True
    )
    @blacklist_check()
    async def _set(self, ctx):
      if ctx.message.author.id == ctx.guild.owner.id:
        embed = discord.Embed(
          title="<a:no:776479189003534346> Incorrect Format!", 
          description="The `set` command has been incorrectly used, for more information on how to use the command do the command: `%toggle`", 
          colour=self.colour
        )
        await ctx.send(embed=embed)
      else:
        await ctx.reply(embed=not_server_owner_msg(), delete_after=15)


    @_set.command(
      name="bans",
      aliases=['antiban']
    )
    @blacklist_check()
    async def toggle_bans(self, ctx, new_toggle_type: str = None):
      if new_toggle_type == None:
        return await ctx.send(embed=create_error_embed("Missing Parameters!\nExample usage: `%toggle ?set antiban on|off`"))
      if not ctx.message.author.id == ctx.guild.owner.id:
        return await ctx.send(embed=not_server_owner_msg())
      type = "Anti-Ban"
      if new_toggle_type.lower() in ("off", "false", "disable"):
        try:
          antitoggle.update_one({'guild_id': ctx.guild.id},{'$set': {'massban': "False"}})
          await ctx.send(embed=create_embed(f'`{type}` Is Now Disabled.'))
        except Exception as e:
          await ctx.send(f"There was an error while changing toggle for: `{type}`")
          raise e
        return
      if new_toggle_type.lower() in ("on", "true", "enable"):
        try:
          antitoggle.update_one({'guild_id': ctx.guild.id},{'$set': {'massban': "True"}})
          await ctx.send(embed=create_embed(f'`{type}` Is Now Enabled.'))
        except Exception as e:
          await ctx.send(f"There was an error while changing toggle for: `{type}`")
          raise e
        return

    @_set.command(
      name="kicks",
      aliases=["antikick"]
    )
    @blacklist_check()
    async def toggle_kicks(self, ctx, new_toggle_type: str = None):
      if new_toggle_type == None:
        return await ctx.send(embed=create_error_embed("Missing Parameters!\nExample usage: `%toggle kicks on|off`"))
      if not ctx.message.author.id == ctx.guild.owner.id:
        return await ctx.send(embed=not_server_owner_msg())
      type = "Anti-Kick"
      if new_toggle_type.lower() in ("off", "false", "disable"):
        try:
          antitoggle.update_one({'guild_id': ctx.guild.id},{'$set': {'masskick': "False"}})
          await ctx.send(embed=create_embed(f'`{type}` Is Now Disabled.'))
        except Exception as e:
          await ctx.send(f"There was an error while changing toggle for: `{type}`")
          raise e
        return
      if new_toggle_type.lower() in ("on", "true", "enable"):
        try:
          antitoggle.update_one({'guild_id': ctx.guild.id},{'$set': {'masskick': "True"}})
          await ctx.send(embed=create_embed(f'`{type}` Is Now Enabled.'))
        except Exception as e:
          await ctx.send(f"There was an error while changing toggle for: `{type}`")
          raise e
        return

    @_set.command(
      name="chan+",
      aliases=["antichannel_create"]
    )
    @blacklist_check()
    async def toggle_chan(self, ctx, new_toggle_type: str = None):
      if new_toggle_type == None:
        return await ctx.send(embed=create_error_embed("Missing Parameters!\nExample usage: `%toggle chan+ on|off`"))
      if not ctx.message.author.id == ctx.guild.owner.id:
        return await ctx.send(embed=not_server_owner_msg())
      type = "Anti-Channel-Create"
      if new_toggle_type.lower() in ("off", "false", "disable"):
        try:
          antitoggle.update_one({'guild_id': ctx.guild.id},{'$set': {'channel_create': "False"}})
          await ctx.send(embed=create_embed(f'`{type}` Is Now Disabled.'))
        except Exception as e:
          await ctx.send(f"There was an error while changing toggle for: `{type}`")
          raise e
        return
      if new_toggle_type.lower() in ("on", "true", "enable"):
        try:
          antitoggle.update_one({'guild_id': ctx.guild.id},{'$set': {'channel_create': "True"}})
          await ctx.send(embed=create_embed(f'`{type}` Is Now Enabled.'))
        except Exception as e:
          await ctx.send(f"There was an error while changing toggle for: `{type}`")
          raise e
        return

    @_set.command(
      name="chan-",
      aliases=["antichannel_delete"]
    )
    @blacklist_check()
    async def toggle_chan_(self, ctx, new_toggle_type: str = None):
      if new_toggle_type == None:
        return await ctx.send(embed=create_error_embed("Missing Parameters!\nExample usage: `%toggle chan- on|off`"))
      if not ctx.message.author.id == ctx.guild.owner.id:
        return await ctx.send(embed=not_server_owner_msg())
      type = "Anti-Channel-Delete"
      if new_toggle_type.lower() in ("off", "false", "disable"):
        try:
          antitoggle.update_one({'guild_id': ctx.guild.id},{'$set': {'channel_delete': "False"}})
          await ctx.send(embed=create_embed(f'`{type}` Is Now Disabled.'))
        except Exception as e:
          await ctx.send(f"There was an error while changing toggle for: `{type}`")
          raise e
        return
      if new_toggle_type.lower() in ("on", "true", "enable"):
        try:
          antitoggle.update_one({'guild_id': ctx.guild.id},{'$set': {'channel_delete': "True"}})
          await ctx.send(embed=create_embed(f'`{type}` Is Now Enabled.'))
        except Exception as e:
          await ctx.send(f"There was an error while changing toggle for: `{type}`")
          raise e
        return

    @_set.command(
      name="role+",
      aliases=["antirole_create"]
    )
    @blacklist_check()
    async def toggle_role(self, ctx, new_toggle_type: str = None):
      if new_toggle_type == None:
        return await ctx.send(embed=create_error_embed("Missing Parameters!\nExample usage: `%toggle role+ on|off`"))
      if not ctx.message.author.id == ctx.guild.owner.id:
        return await ctx.send(embed=not_server_owner_msg())
      type = "Anti-Role-Create"
      if new_toggle_type.lower() in ("off", "false", "disable"):
        try:
          antitoggle.update_one({'guild_id': ctx.guild.id},{'$set': {'role_create': "False"}})
          await ctx.send(embed=create_embed(f'`{type}` Is Now Disabled.'))
        except Exception as e:
          await ctx.send(f"There was an error while changing toggle for: `{type}`")
          raise e
        return
      if new_toggle_type.lower() in ("on", "true", "enable"):
        try:
          antitoggle.update_one({'guild_id': ctx.guild.id},{'$set': {'role_create': "True"}})
          await ctx.send(embed=create_embed(f'`{type}` Is Now Enabled.'))
        except Exception as e:
          await ctx.send(f"There was an error while changing toggle for: `{type}`")
          raise e
        return

    @_set.command(
      name="role-",
      aliases=["antirole_delete"]
    )
    @blacklist_check()
    async def toggle_role_(self, ctx, new_toggle_type: str = None):
      if new_toggle_type == None:
        return await ctx.send(embed=create_error_embed("Missing Parameters!\nExample usage: `%toggle role- on|off`"))
      if not ctx.message.author.id == ctx.guild.owner.id:
        return await ctx.send(embed=not_server_owner_msg())
      type = "Anti-Role-Delete"
      if new_toggle_type.lower() in ("off", "false", "disable"):
        try:
          antitoggle.update_one({'guild_id': ctx.guild.id},{'$set': {'role_delete': "False"}})
          await ctx.send(embed=create_embed(f'`{type}` Is Now Disabled.'))
        except Exception as e:
          await ctx.send(f"There was an error while changing toggle for: `{type}`")
          raise e
        return
      if new_toggle_type.lower() in ("on", "true", "enable"):
        try:
          antitoggle.update_one({'guild_id': ctx.guild.id},{'$set': {'role_delete': "True"}})
          await ctx.send(embed=create_embed(f'`{type}` Is Now Enabled.'))
        except Exception as e:
          await ctx.send(f"There was an error while changing toggle for: `{type}`")
          raise e
        return

    @_set.command(
      name="webhook",
      aliases=["antiwebhook"]
    )
    @blacklist_check()
    async def toggle_webhook(self, ctx, new_toggle_type: str = None):
      if new_toggle_type == None:
        return await ctx.send(embed=create_error_embed("Missing Parameters!\nExample usage: `%toggle webhooks on|off`"))
      if not ctx.message.author.id == ctx.guild.owner.id:
        return await ctx.send(embed=not_server_owner_msg())
      type = "Anti-Webhook"
      if new_toggle_type.lower() in ("off", "false", "disable"):
        try:
          antitoggle.update_one({'guild_id': ctx.guild.id},{'$set': {'webhook_ud': "False"}})
          await ctx.send(embed=create_embed(f'`{type}` Is Now Disabled.'))
        except Exception as e:
          await ctx.send(f"There was an error while changing toggle for: `{type}`")
          raise e
        return
      if new_toggle_type.lower() in ("on", "true", "enable"):
        try:
          antitoggle.update_one({'guild_id': ctx.guild.id},{'$set': {'webhook_ud': "True"}})
          await ctx.send(embed=create_embed(f'`{type}` Is Now Enabled.'))
        except Exception as e:
          await ctx.send(f"There was an error while changing toggle for: `{type}`")
          raise e
        return

    @_set.command(
      name="vanityprot",
      aliases=['vanity', 'vanityprotection', 'antivanity']
    )
    @blacklist_check()
    async def toggle_vanityprot(self, ctx, new_toggle_type: str = None):
      if new_toggle_type == None:
        return await ctx.send(embed=create_error_embed("Missing Parameters!\nExample usage: `%toggle vanity on|off`"))
      if not ctx.message.author.id == ctx.guild.owner.id:
        return await ctx.send(embed=not_server_owner_msg())
      type = "Anti-Vanity-Protection"
      if new_toggle_type.lower() in ("off", "false", "disable"):
        try:
          antitoggle.update_one({'guild_id': ctx.guild.id},{'$set': {'vanity_protect': "False"}})
          await ctx.send(embed=create_embed(f'`{type}` Is Now Disabled.'))
        except Exception as e:
          await ctx.send(f"There was an error while changing toggle for: `{type}`")
          raise e
        return
      if new_toggle_type.lower() in ("on", "true", "enable"):
        try:
          antitoggle.update_one({'guild_id': ctx.guild.id},{'$set': {'vanity_protect': "True"}})
          await ctx.send(embed=create_embed(f'`{type}` Is Now Enabled.'))
        except Exception as e:
          await ctx.send(f"There was an error while changing toggle for: `{type}`")
          raise e
        return

"""
    @_set.command(
      name="bot",
      aliases=["bots", "antibot"]
    )
    @blacklist_check()
    async def toggle_bot(self, ctx, new_toggle_type: str = None):
      if new_toggle_type == None:
        return await ctx.send(embed=create_error_embed("Missing Parameters!\nExample usage: `%toggle bot on|off`"))
      if not ctx.message.author.id == ctx.guild.owner.id:
        return await ctx.send(embed=not_server_owner_msg())
      type = "Anti-Bot"
      if new_toggle_type.lower() in ("off", "false", "disable"):
        try:
          antitoggle.update_one({'guild_id': ctx.guild.id},{'$set': {'webhook_ud': "False"}})
          await ctx.send(embed=create_embed(f'`{type}` Is Now Disabled.'))
        except Exception as e:
          await ctx.send(f"There was an error while changing toggle for: `{type}`")
          raise e
        return
      if new_toggle_type.lower() in ("on", "true", "enable"):
        try:
          antitoggle.update_one({'guild_id': ctx.guild.id},{'$set': {'webhook_ud': "True"}})
          await ctx.send(embed=create_embed(f'`{type}` Is Now Enabled.'))
        except Exception as e:
          await ctx.send(f"There was an error while changing toggle for: `{type}`")
          raise e
        return
"""


def setup(client):
    client.add_cog(Toggles(client))