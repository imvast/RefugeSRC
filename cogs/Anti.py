# IMPORTS #
from aiohttp.helpers import MimeType
import discord, os, motor.motor_asyncio, datetime, datetime, time, aiohttp
from Utils.utils import utils 
from colorama import Fore as C
from colorama import Fore
from discord.ext import commands, tasks
from settings import *

# Connect to MongoDB
mongoClient = motor.motor_asyncio.AsyncIOMotorClient(os.environ.get('BOT_DB'))
db = mongoClient['refuge']['server-data']
db2 = mongoClient['refuge']
antitoggle = db2['antitoggle']
blacklist = db2['blacklist']
gprefix = db['prefix']

def blacklist_check():
    async def predicate(ctx):
        author_id = ctx.author.id
        if await blacklist.find_one({'user_id': author_id}):
            return False
        return True
    return commands.check(predicate)


class Anti(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.db = db
        self.colour = 0x2F3136
        print(f"{C.CYAN}[Status] Cog Loaded: Anti" + C.RESET)



    # anti mass-channel-deletion
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
      data = await antitoggle.find_one({ "guild_id": channel.guild.id })
      if data["channel_delete"] != "True":
        return
      data = await db.find_one({ "guild_id": channel.guild.id })
      punishment = data["punishment"]
      whitelistedUsers = data["user_whitelist"]
      logschannelid = data["logs_channel"]
      logschannel = self.client.get_channel(logschannelid)
      try:
       async for entry in channel.guild.audit_logs(limit=1, after=datetime.datetime.now() - datetime.timedelta(seconds = 3), action=discord.AuditLogAction.channel_delete):
        if entry.user.id == self.client.user.id:
          return
        if entry.user.id in whitelistedUsers:
          if data["dm_logs"] == "True" and entry.user != channel.guild.owner:
            await channel.guild.owner.send(embed=create_embed(f"<:r_alert:860644383535267850> This is a beta feature.\nA user has triggered my protection system: {entry.user} => No actions have been taken as they are whitelisted."))
          if logschannel != None:
            embed = discord.Embed(
              title=f"[refuge logs]: Channel Deleted. (authorized)", 
              description=f"<a:R_Arrow:767064076512919552> Channel: {channel.name} | `{channel.id}`\n<a:R_Arrow:767064076512919552> Deleted by: {entry.user.name} | `{entry.user.id}`\n<a:R_Arrow:767064076512919552> Actions Taken: `None`",
              colour=self.colour
            )
            await logschannel.send(embed=embed)
          return
        try:
            if punishment == 'kick':
              await entry.user.kick(reason="[refuge protection]\n・User Caught Deleting Channels.")
              if logschannel != None:
                embed = discord.Embed(
                  title=f"[Refuge Logs System] Channel Deleted. (unauthorized)", 
                  description=f"<a:R_Arrow:767064076512919552> Channel: {channel.name} | `{channel.id}`\n<a:R_Arrow:767064076512919552> Deleted by: {entry.user.name} | `{entry.user.id}`\n<a:R_Arrow:767064076512919552> Action Taken: `{punishment}`",
                  colour=self.colour
                )
                await logschannel.send(embed=embed)
            if punishment == 'ban':
              await entry.user.ban(reason="[refuge protection]\n・User Caught Deleting Channels.")
              if logschannel != None:
                embed = discord.Embed(
                  title=f"[Refuge Logs System] Channel Deleted. (unauthorized)", 
                  description=f"<a:R_Arrow:767064076512919552> Channel: {channel.name} | `{channel.id}`\n<a:R_Arrow:767064076512919552> Deleted by: {entry.user.name} | `{entry.user.id}`\n<a:R_Arrow:767064076512919552> Action Taken: `{punishment}`",
                  colour=self.colour
                )
                await logschannel.send(embed=embed)
            if data["dm_logs"] == "True" and entry.user != channel.guild.owner:
              await channel.guild.owner.send(f"<:r_alert:860644383535267850> A non-whitelisted user has triggered my protection system: {entry.user} => The channel deleted was {channel.name} | {channel.id}. As a part of our anti-nuke on refuge, the channel deleted has been recreated and your server has been restored back to normal.")
            return
        except Exception as error:
            if isinstance(error, discord.Forbidden):
              return
            else:
              return print(f"{Fore.RED}[Anti Error]: Deleted Channel. ({channel.guild.name}){Fore.RESET}") 
      except Exception as error:
        if isinstance(error, discord.Forbidden):
          return
        else:
          return print(f"{Fore.RED}[Anti Error]: {error} | Anti-Channel-Delete. ({channel.guild.name}){Fore.RESET}") 

    # anti mass-channel
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
      data = await antitoggle.find_one({ "guild_id": channel.guild.id })
      if data["channel_create"] != "True":
        return
      data = await db.find_one({ "guild_id": channel.guild.id })
      punishment = data["punishment"]
      whitelistedUsers = data["user_whitelist"]
      logschannelid = data["logs_channel"]
      logschannel = self.client.get_channel(logschannelid)
      try:
       async for entry in channel.guild.audit_logs(limit=1, after=datetime.datetime.now() - datetime.timedelta(seconds = 3), action=discord.AuditLogAction.channel_create):
        if entry.user.id == self.client.user.id:
          return
        if entry.user.id in whitelistedUsers:
          if data["dm_logs"] == "True" and entry.user != channel.guild.owner:
            await channel.guild.owner.send(embed=create_embed(f"<:r_alert:860644383535267850> This is a beta feature.\nA user has triggered my protection system: {entry.user} => No actions have been taken as they are whitelisted."))
          if logschannel != None:
            embed = discord.Embed(
              title=f"[refuge logs]: Channel Created. (authorized)", 
              description=f"<a:R_Arrow:767064076512919552> Channel: {channel.name} | `{channel.id}`\n<a:R_Arrow:767064076512919552> Created by: {entry.user.name} | `{entry.user.id}`\n<a:R_Arrow:767064076512919552> Actions Taken: `None`",
              colour=self.colour
            )
            await logschannel.send(embed=embed)
          return
        try:
            if punishment == 'kick':
              await entry.user.kick(reason="[refuge protection]\n・User Caught Creating Channels.")
              if logschannel != None:
                embed = discord.Embed(
                  title=f"[refuge logs] Channel Created. (unauthorized)", 
                  description=f"<a:R_Arrow:767064076512919552> Channel: {channel.name} | `{channel.id}`\n<a:R_Arrow:767064076512919552> Created by: {entry.user.name} | `{entry.user.id}`\n<a:R_Arrow:767064076512919552> Action Taken: `{punishment}`",
                  colour=self.colour
                )
                await logschannel.send(embed=embed)
            if punishment == 'ban':
              await entry.user.ban(reason="[refuge protection]\n・User Caught Creating Channels.")
              if logschannel != None:
                embed = discord.Embed(
                  title=f"[refuge logs] Channel Created. (unauthorized)", 
                  description=f"<a:R_Arrow:767064076512919552> Channel: {channel.name} | `{channel.id}`\n<a:R_Arrow:767064076512919552> Created by: {entry.user.name} | `{entry.user.id}`\n<a:R_Arrow:767064076512919552> Action Taken: `{punishment}`",
                  colour=self.colour
                )
                await logschannel.send(embed=embed)
            langs = ["Python", "Javascript", "GoLang", "Rust", ""]
            embed = discord.Embed()
            for lang in langs:
              embed.add_field(name=lang, value="Don't use %s use brainfuck" % (lang))
            await entry.user.send(embed=embed, content="imagine trying to nuke `{}`\nyou must be a retard.".format(channel.guild.name))
            await channel.delete()
        except Exception as error:
            if isinstance(error, discord.Forbidden):
              return
            else:
              return print(f"{Fore.RED}[Anti Error]: Created Channel. ({channel.guild.name}) | {error}{Fore.RESET}") 
      except Exception as error:
        if isinstance(error, discord.Forbidden):
          return
        else:
          return print(f"{Fore.RED}[Anti Error]: {error} | Anti-Channel-Create. ({channel.guild.name}){Fore.RESET}") 

    # anti ban
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
      beforeutc = time.perf_counter()
      data = await antitoggle.find_one({ "guild_id": guild.id })
      if data["massban"] != "True":
        return
      headers = {"Authorization": f"Bot {os.environ.get('BOT_TOKEN')}"}
      reason = {'reason': '[refuge protection]\n・User Caught Banning Members.'}
      data = await db.find_one({ "guild_id": guild.id })
      punishment = data["punishment"]
      whitelistedUsers = data["user_whitelist"]
      logschannelid = data["logs_channel"]
      logschannel = self.client.get_channel(logschannelid)
      after_punish = False
      async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(f'https://discord.com/api/v9/guilds/{guild.id}/audit-logs?limit=1&action_type=22', headers=headers) as resp:
          respjson = await resp.json()
          entry = respjson['audit_log_entries'][0]
        entryuser = self.client.get_user(int(entry['user_id']))
        if str(entry['user_id']) == str(self.client.user.id):
          return
        else:
          print(entry)
          if str(entry['user_id']) in str(whitelistedUsers):
            if data["dm_logs"] == "True" and entryuser != guild.owner:
              embed = utils.format_antilogs(dm=True, user=entryuser, guild=guild, actionon="user banned", action="none : whitelisted", rms="0")
              await guild.owner.send(embed=embed)
            if logschannel != None:
              embed = discord.Embed(
                title=f"[refuge logs]: Member Banned. (authorized)", 
                description=f"<a:R_Arrow:767064076512919552> Member: {user.name} | `{user.id}`\n<a:R_Arrow:767064076512919552> Banned by: {entryuser} | `{entry['user_id']}`\n<a:R_Arrow:767064076512919552> Actions Taken: `None`",
                colour=self.colour
              )
              await logschannel.send(embed=embed)
            return
          try:
            async with aiohttp.ClientSession(headers=headers) as session:
              if punishment == 'ban':
                async with session.put(f"https://discord.com/api/v9/guilds/{guild.id}/bans/{entry['user_id']}", headers=headers, json=reason) as resp:
                  responsestatus = resp.status
                  responsetext = resp.text
                after_punish = True; afterutc = time.perf_counter()
              if punishment == 'kick':
                async with session.delete(f"https://discord.com/api/v9/guilds/{guild.id}/members/{entry['user_id']}", headers=headers, json=reason) as resp:
                  responsestatus = await resp.json(content_type=None)
                after_punish = True; afterutc = time.perf_counter()
              if responsestatus not in (200,201,204) and responsestatus != 403:
                if punishment == 'ban':
                  return print(f"!! error for anti-ban (ban) | {responsestatus}")
                if punishment == 'kick':
                  return print(f"!! error for anti-ban (kick) | {responsestatus}")
              elif responsestatus == 429 or responsetext['retry_after'] != None:
                time.sleep(responsetext['retry_after']) 
                if punishment == 'ban':
                  session.put(f"https://discord.com/api/v9/guilds/{guild.id}/bans/{entry['user_id']}", headers=headers, json=reason)
                if punishment == 'kick':
                  session.delete(f"https://discord.com/api/v9/guilds/{guild.id}/members/{entry['user_id']}", headers=headers, json=reason)
            if after_punish == True:
              if logschannel != None:
                responsetime = afterutc - beforeutc
                embed = utils.format_antilogs(dm=False, user=entryuser, guild=guild, actionon=user, action=punishment, rms=responsetime)
                #embed = discord.Embed(
                  #title=f"[refuge logs] Unauthorized Ban!", 
                  #description=f"<a:R_Arrow:767064076512919552> Member: {user.name} | `{user.id}`\n<a:R_Arrow:767064076512919552> Banned by: {entryuser.name} | `{entry['user_id']}`\n<a:R_Arrow:767064076512919552> Action Taken: `{punishment}`",#\n<a:R_Arrow:767064076512919552> Responded in: `{end_time - start_time:0.4f} second(s)`",
                  #colour=self.colour
                #)
                await logschannel.send(embed=embed)
          except Exception as error:
            if isinstance(error, discord.Forbidden):
              pass
            else:
              return print(f"{Fore.RED}[Anti Error]: {error} (Anti-Ban) ({guild.name}){Fore.RESET}") 
      #except Exception as error:
        #if isinstance(error, discord.Forbidden):
          #pass
        #else:
          #return print(f"{Fore.RED}[Anti Error]: {error} | Anti-Ban. ({guild.name}){Fore.RESET}") 


    # anti kick
    @commands.Cog.listener()
    async def on_member_remove(self, member):
      data = await antitoggle.find_one({ "guild_id": member.guild.id })
      if data["masskick"] != "True":
        return
      data = await db.find_one({ "guild_id": member.guild.id })
      punishment = data["punishment"]
      whitelistedUsers = data["user_whitelist"]
      logschannelid = data["logs_channel"]
      logschannel = self.client.get_channel(logschannelid)
      try:
        async for entry in member.guild.audit_logs(limit=1, after=datetime.datetime.now() - datetime.timedelta(seconds = 3)):
          if entry.user.id == self.client.user.id:
            return
          if entry.action == discord.AuditLogAction.kick:
            if entry.user.id in whitelistedUsers:
              if data["dm_logs"] == "True" and entry.user != member.guild.owner:
                await member.guild.owner.send(f"<:r_alert:860644383535267850> This is a beta feature.\nA user has triggered my protection system: {entry.user} => No actions have been taken as they are whitelisted.")
              if logschannel != None:
                embed = discord.Embed(
                  title=f"[refuge logs]: Member Kicked. (authorized)", 
                  description=f"<a:R_Arrow:767064076512919552> Member: {member.name} | `{member.id}`\n<a:R_Arrow:767064076512919552> Removed by: {entry.user.name} | `{entry.user.id}`\n<a:R_Arrow:767064076512919552> Actions Taken: `None`",
                  colour=self.colour
                )
                await logschannel.send(embed=embed)
              return
            try:
                if punishment == 'kick':
                  await entry.user.kick(reason="[refuge protection]\n・User Caught Kicking Members.")
                  if logschannel != None:
                    embed = discord.Embed(
                      title=f"[refuge logs] Member Kicked. (unauthorized)", 
                      description=f"<a:R_Arrow:767064076512919552> Member: {member.name} | `{member.id}`\n<a:R_Arrow:767064076512919552> Removed by: {entry.user.name} | `{entry.user.id}`\n<a:R_Arrow:767064076512919552> Action Taken: `{punishment}`",
                      colour=self.colour
                    )
                    await logschannel.send(embed=embed)
                if punishment == 'ban':
                  await entry.user.ban(reason="[refuge protection]\n・User Caught Kicking Members.")
                  if logschannel != None:
                    embed = discord.Embed(
                      title=f"[refuge logs] Member Kicked. (unauthorized)", 
                      description=f"<a:R_Arrow:767064076512919552> Member: {member.name} | `{member.id}`\n<a:R_Arrow:767064076512919552> Removed by: {entry.user.name} | `{entry.user.id}`\n<a:R_Arrow:767064076512919552> Action Taken: `{punishment}`",
                      colour=self.colour
                    )
                    await logschannel.send(embed=embed)
            except Exception as error:
                if isinstance(error, discord.Forbidden):
                  return
                else:
                  return print(f"{Fore.RED}[Anti Error]: Kicked Member. ({member.guild.name}){Fore.RESET}") 
          elif entry.action == discord.AuditLogAction.member_prune:
            if entry.user.id == self.client.user.id:
              return
            if entry.user.id in whitelistedUsers:
              if data["dm_logs"] == "True" and entry.user != member.guild.owner:
                await member.guild.owner.send(f"<:r_alert:860644383535267850> This is a beta feature.\nA user has triggered my protection system: {entry.user} => No actions have been taken as they are whitelisted.")
              if logschannel != None:
                embed = discord.Embed(
                  title=f"[refuge logs]: Prune Detection. (authorized)", 
                  description=f"<a:R_Arrow:767064076512919552> Pruned by: {entry.user.name} | `{entry.user.id}`\n<a:R_Arrow:767064076512919552> Actions Taken: `None`",
                  colour=self.colour
                )
                await logschannel.send(embed=embed)
              return
            try:
                if punishment == 'kick':
                  await entry.user.kick(reason="[refuge protection]\n・User Caught Kicking Members.")
                  if logschannel != None:
                    embed = discord.Embed(
                      title=f"[refuge logs] Prune Detection. (unauthorized)", 
                      description=f"<a:R_Arrow:767064076512919552> Pruned by: {entry.user.name} | `{entry.user.id}`\n<a:R_Arrow:767064076512919552> Action Taken: `{punishment}`",
                      colour=self.colour
                    )
                    await logschannel.send(embed=embed)
                if punishment == 'ban':
                  await entry.user.ban(reason="[refuge protection]\n・User Caught Kicking Members.")
                  if logschannel != None:
                    embed = discord.Embed(
                      title=f"[refuge logs] Prune Detection. (unauthorized)", 
                      description=f"<a:R_Arrow:767064076512919552> Pruned by: {entry.user.name} | `{entry.user.id}`\n<a:R_Arrow:767064076512919552> Action Taken: `{punishment}`",
                      colour=self.colour
                    )
                    await logschannel.send(embed=embed)
            except Exception as error:
              if isinstance(error, discord.Forbidden):
                return
              else:
                return print(f"{Fore.RED}[Anti Error]: Pruned Members. ({member.guild.name}){Fore.RESET}") 
        else:
          return
      except Exception as error:
        if isinstance(error, discord.Forbidden):
          return
        else:
          return print(f"{Fore.RED}[Anti Error]: {error} | Anti-Remove. ({member.guild.name}){Fore.RESET}") 


    # anti webhook
    @commands.Cog.listener()
    async def on_webhooks_update(self, channel):
      data = await antitoggle.find_one({ "guild_id": channel.guild.id })
      if data["webhook_ud"] != "True":
        return
      data = await db.find_one({ "guild_id": channel.guild.id })
      punishment = data["punishment"]
      whitelistedUsers = data["user_whitelist"]
      logschannelid = data["logs_channel"]
      logschannel = self.client.get_channel(logschannelid)
      try:
       async for entry in channel.guild.audit_logs(limit=1, after=datetime.datetime.now() - datetime.timedelta(seconds = 3)):
        if entry.action != discord.AuditLogAction.webhook_create:
          return
        else:
          if entry.user.id == self.client.user.id:
            return
          if entry.user.id in whitelistedUsers:
            if data["dm_logs"] == "True" and entry.user != channel.guild.owner:
              await channel.guild.owner.send(embed=create_embed(f"<:r_alert:860644383535267850> This is a beta feature.\nA user has triggered my protection system: {entry.user} => No actions have been taken as they are whitelisted."))
            if logschannel != None:
              embed = discord.Embed(
                title=f"[refuge logs]: Webhook Created. (authorized)", 
                description=f"<a:R_Arrow:767064076512919552> Webhook: Unkown | `Unkown`\n<a:R_Arrow:767064076512919552> Created by: {entry.user.name} | `{entry.user.id}`\n<a:R_Arrow:767064076512919552> Created in: `{channel.name}` | `{channel.id}`\n<a:R_Arrow:767064076512919552> Actions Taken: `None`",
                colour=self.colour
              )
              await logschannel.send(embed=embed)
            return
          try:
            if punishment == 'kick':
              await entry.user.kick(reason="[refuge protection]\n・User Caught Creating Webhooks.")
              if logschannel != None:
                embed = discord.Embed(
                  title=f"[refuge logs] Webhook Created. (unauthorized)", 
                  description=f"<a:R_Arrow:767064076512919552> Webhook: Unkown | `Unkown`\n<a:R_Arrow:767064076512919552> Created by: {entry.user.name} | `{entry.user.id}`\n<a:R_Arrow:767064076512919552> Created in: `{channel.name}` | `{channel.id}`\n<a:R_Arrow:767064076512919552> Action Taken: `{punishment}`",
                  colour=self.colour
                )
                await logschannel.send(embed=embed)
            if punishment == 'ban':
              await entry.user.ban(reason="[refuge protection]\n・User Caught Creating Webhooks.")
              if logschannel != None:
                embed = discord.Embed(
                  title=f"[refuge logs] Webhook Created. (unauthorized)", 
                  description=f"<a:R_Arrow:767064076512919552> Webhook: Unkown | `Unkown`\n<a:R_Arrow:767064076512919552> Created by: {entry.user.name} | `{entry.user.id}`\n<a:R_Arrow:767064076512919552> Created in: `{channel.name}` | `{channel.id}`\n<a:R_Arrow:767064076512919552> Action Taken: `{punishment}`",
                  colour=self.colour
                )
                await logschannel.send(embed=embed)
            await entry.target.delete()
          except Exception as error:
            if isinstance(error, discord.Forbidden):
              return
            else:
              return print(f"{Fore.RED}[Anti Error]: Webhook Creation. ({channel.guild.name}){Fore.RESET}") 
      except Exception as error:
        if isinstance(error, discord.Forbidden):
          return
        else:
          return print(f"{Fore.RED}[Anti Error]: {error} | Anti-Webhook. ({channel.guild.name}){Fore.RESET}") 


    # anti bot
    @commands.Cog.listener()
    async def on_member_join(self, member):
      #data = await antitoggle.find_one({ "guild_id": channel.guild.id })
      #if data["antibot"] != "True":
        #return
      data = await db.find_one({ "guild_id": member.guild.id })
      punishment = data["punishment"]
      whitelistedUsers = data["user_whitelist"]
      logschannelid = data["logs_channel"]
      logschannel = self.client.get_channel(logschannelid)
      if member.bot:
        try:
          async for entry in member.guild.audit_logs(limit=1, after=datetime.datetime.now() - datetime.timedelta(seconds = 3), action=discord.AuditLogAction.bot_add):
            if entry.user.id == self.client.user.id:
              return
            if entry.user.id in whitelistedUsers:
              if data["dm_logs"] == "True" and entry.user != member.guild.owner:
                await member.guild.owner.send(f"<:r_alert:860644383535267850> This is a beta feature.\nA user has triggered my protection system: {entry.user} => No actions have been taken as they are whitelisted.")
              if logschannel != None:
                embed = discord.Embed(
                  title=f"[refuge logs]: Bot Added. (authorized)", 
                  description=f"<a:R_Arrow:767064076512919552> Bot: {member.name} | `{member.id}`\n<a:R_Arrow:767064076512919552> Added by: {entry.user.name} | `{entry.user.id}`\n<a:R_Arrow:767064076512919552> Actions Taken: `None`",
                  colour=self.colour
                )
                await logschannel.send(embed=embed)
              return 
            try:
              if punishment == 'kick':
                await member.kick(reason="[refuge protection]\n・Anti-Bot is enabled.")
                await entry.user.kick(reason="[refuge protection]\n・User Caught Adding Bots.")
                if logschannel != None:
                  embed = discord.Embed(
                    title=f"[refuge logs] Bot Added. (unauthorized)", 
                    description=f"<a:R_Arrow:767064076512919552> Bot: {member.name} | `{member.id}`\n<a:R_Arrow:767064076512919552> Added by: {entry.user.name} | `{entry.user.id}`\n<a:R_Arrow:767064076512919552> Action Taken: `{punishment}`",
                  )
                await logschannel.send(embed=embed)
              if punishment == 'ban':
                await member.ban(reason="[refuge protection]\n・Anti-Bot is enabled.")
                await entry.user.ban(reason="[refuge protection]\n・User Caught Adding Bots.")
                if logschannel != None:
                  embed = discord.Embed(
                    title=f"[refuge logs] Bot Added. (unauthorized)", 
                    description=f"<a:R_Arrow:767064076512919552> Bot: {member.name} | `{member.id}`\n<a:R_Arrow:767064076512919552> Added by: {entry.user.name} | `{entry.user.id}`\n<a:R_Arrow:767064076512919552> Action Taken: `{punishment}`",
                    colour=self.colour
                  )
                  await logschannel.send(embed=embed)
            except Exception as error:
              if isinstance(error, discord.Forbidden):
                return
              else:
                return print(f"{Fore.RED}[Anti Error]: Added Bot. ({member.guild.name}){Fore.RESET}")
        except Exception as error:
          if isinstance(error, discord.Forbidden):
            return
          else:
            return print(f"{Fore.RED}[Anti Error]: {error} | Anti-Bot. ({member.guild.name}){Fore.RESET}") 

    # anti mass-role
    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
      data = await antitoggle.find_one({ "guild_id": role.guild.id })
      if data["role_create"] != "True":
        return
      data = await db.find_one({ "guild_id": role.guild.id })
      punishment = data["punishment"]
      whitelistedUsers = data["user_whitelist"]
      logschannelid = data["logs_channel"]
      logschannel = self.client.get_channel(logschannelid)
      try:
       async for entry in role.guild.audit_logs(limit=1, after=datetime.datetime.now() - datetime.timedelta(seconds = 3), action=discord.AuditLogAction.role_create):
        if entry.user.id == self.client.user.id:
          return
        if entry.user.id in whitelistedUsers:
          if data["dm_logs"] == "True" and entry.user != role.guild.owner:
            await role.guild.owner.send(f"<:r_alert:860644383535267850> This is a beta feature.\nA user has triggered my protection system: {entry.user} => No actions have been taken as they are whitelisted.")
          if logschannel != None:
            embed = discord.Embed(
              title=f"[refuge logs]: Role Created. (authorized)", 
              description=f"<a:R_Arrow:767064076512919552> Role: {role.name} | `{role.id}`\n<a:R_Arrow:767064076512919552> Created by: {entry.user.name} | `{entry.user.id}`\n<a:R_Arrow:767064076512919552> Actions Taken: `None`",
              colour=self.colour
            )
            await logschannel.send(embed=embed)
          return
        try:
            if punishment == 'kick':
              await role.guild.kick(entry.user, reason="[refuge protection]\n・User Caught Creating Roles.")
              if logschannel != None:
                embed = discord.Embed(
                  title=f"[refuge logs] Role Created. (unauthorized)", 
                  description=f"<a:R_Arrow:767064076512919552> Role: {role.name} | `{role.id}`\n<a:R_Arrow:767064076512919552> Created by: {entry.user.name} | `{entry.user.id}`\n<a:R_Arrow:767064076512919552> Action Taken: `{punishment}`",
                  colour=self.colour
                )
                await logschannel.send(embed=embed)
            if punishment == 'ban':
              await entry.user.ban(reason="[refuge protection]\n・User Caught Creating Roles.")
              if logschannel != None:
                embed = discord.Embed(
                  title=f"[refuge logs] Role Created. (unauthorized)", 
                  description=f"<a:R_Arrow:767064076512919552> Role: {role.name} | `{role.id}`\n<a:R_Arrow:767064076512919552> Created by: {entry.user.name} | `{entry.user.id}`\n<a:R_Arrow:767064076512919552> Action Taken: `{punishment}`",
                  colour=self.colour
                )
                await logschannel.send(embed=embed)
        except Exception as error:
            if isinstance(error, discord.Forbidden):
              return
            else:
              return print(f"{Fore.RED}[Anti Error]: Role-Creation. ({role.guild.name}){Fore.RESET}")
      except Exception as error:
        if isinstance(error, discord.Forbidden):
          return
        else:
          return print(f"{Fore.RED}[Anti Error]: {error} | Anti-Role-Create. ({role.guild.name}){Fore.RESET}") 

    # anti mass-role-deletion
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
      data = await antitoggle.find_one({ "guild_id": role.guild.id })
      if data["role_delete"] != "True":
        return
      data = await db.find_one({ "guild_id": role.guild.id })
      punishment = data["punishment"]
      whitelistedUsers = data["user_whitelist"]
      logschannelid = data["logs_channel"]
      logschannel = self.client.get_channel(logschannelid)
      try:
       async for entry in role.guild.audit_logs(limit=1, after=datetime.datetime.now() - datetime.timedelta(seconds = 3), action=discord.AuditLogAction.role_delete):
        if entry.user.id == self.client.user.id:
          return
        if entry.user.id in whitelistedUsers:
          if data["dm_logs"] == "True" and entry.user != role.guild.owner:
            await role.guild.owner.send(f"<:r_alert:860644383535267850> This is a beta feature.\nA user has triggered my protection system: {entry.user} => No actions have been taken as they are whitelisted.")
          if logschannel != None:
            embed = discord.Embed(
              title=f"[refuge logs]: Role Deleted. (authorized)", 
              description=f"<a:R_Arrow:767064076512919552> Role: {role.name} | `{role.id}`\n<a:R_Arrow:767064076512919552> Deleted by: {entry.user.name} | `{entry.user.id}`\n<a:R_Arrow:767064076512919552> Actions Taken: `None`",
              colour=self.colour
            )
            await logschannel.send(embed=embed)
          return
        try:
            if punishment == 'kick':
              await role.guild.kick(entry.user, reason="[refuge protection]\n・User Caught Deleting Roles.")
              if logschannel != None:
                embed = discord.Embed(
                  title=f"[refuge logs] Role Deleted. (unauthorized)", 
                  description=f"<a:R_Arrow:767064076512919552> Role: {role.name} | `{role.id}`\n<a:R_Arrow:767064076512919552> Deleted by: {entry.user.name} | `{entry.user.id}`\n<a:R_Arrow:767064076512919552> Action Taken: `{punishment}`",
                  colour=self.colour
                )
                await logschannel.send(embed=embed)
            if punishment == 'ban':
              await role.guild.ban(entry.user, reason="[refuge protection]\n・User Caught Deleting Roles.")
              if logschannel != None:
                embed = discord.Embed(
                  title=f"[refuge logs] Role Deleted. (unauthorized)", 
                  description=f"<a:R_Arrow:767064076512919552> Role: {role.name} | `{role.id}`\n<a:R_Arrow:767064076512919552> Deleted by: {entry.user.name} | `{entry.user.id}`\n<a:R_Arrow:767064076512919552> Action Taken: `{punishment}`",
                  colour=self.colour
                )
                await logschannel.send(embed=embed)
        except Exception as error:
            if isinstance(error, discord.Forbidden):
              return
            else:
              return print(f"{Fore.RED}[Anti Error]: Role-Deletion. ({role.guild.name}){Fore.RESET}")
      except Exception as error:
        if isinstance(error, discord.Forbidden):
          return
        else:
          return print(f"{Fore.RED}[Anti Error]: {error} | Anti-Role-Delete. ({role.guild.name}){Fore.RESET}") 

    # anti permissions
    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        #data = await antitoggle.find_one({ "guild_id": after.guild.id })
        #if data["role_permissions"] != "True":
          #return
        data = await db.find_one({ "guild_id": after.guild.id })
        punishment = data["punishment"]
        whitelistedUsers = data["user_whitelist"]
        logschannelid = data["logs_channel"]
        logschannel = self.client.get_channel(logschannelid)
        try:
         async for entry in after.guild.audit_logs(limit=1, after=datetime.datetime.now() - datetime.timedelta(seconds = 3)):
          if entry.action != discord.AuditLogAction.role_update:
            return
          else:
            if entry.user.id == self.client.user.id:
              return
            if entry.user.id in whitelistedUsers:
              if data["dm_logs"] == "True" and entry.user != after.guild.owner:
                await after.guild.owner.send(f"<:r_alert:860644383535267850> This is a beta feature.\nA user has triggered my protection system: {entry.user} => No actions have been taken as they are whitelisted.")
              if logschannel != None:
                embed = discord.Embed(
                  title=f"[refuge logs]: Role Permissions Updated. (authorized)", 
                  description=f"<a:R_Arrow:767064076512919552> Role: {after.name} | `{after.id}`\n<a:R_Arrow:767064076512919552> Updated by: {entry.user.name} | `{entry.user.id}`\n<a:R_Arrow:767064076512919552> Actions Taken: `None`",
                  colour=self.colour
                )
                await logschannel.send(embed=embed)
              return

            if not before.permissions.ban_members and after.permissions.ban_members:
                try:
                  if punishment == 'kick':
                    await after.guild.kick(entry.user, reason="[refuge protection]\n・User Caught Giving Role Unsafe Permissions")
                    await after.edit(permissions=1166401)
                    return
                  if punishment == 'ban':
                    await after.guild.ban(entry.user, reason="[refuge protection]\n・User Caught Giving Role Unsafe Permissions..")
                    await after.edit(permissions=1166401)
                    return
                except Exception as error:
                  if isinstance(error, discord.Forbidden):
                    return
                  else:
                    return print(f"{Fore.RED}[Anti Error]: Ban-Permissions ({after.guild.name}){Fore.RESET}")

            if not before.permissions.kick_members and after.permissions.kick_members:
                try:
                    if punishment == 'kick':
                      await after.guild.kick(entry.user, reason="[refuge protection]\n・User Caught Giving Role Unsafe Permissions.")
                      await after.edit(permissions=1166401)
                      return
                    if punishment == 'ban':
                      await after.guild.ban(entry.user, reason="[refuge protection]\n・User Caught Giving Role Unsafe Permissions.")
                      await after.edit(permissions=1166401)
                      return
                except Exception as error:
                    if isinstance(error, discord.Forbidden):
                      return
                    else:
                      return print(f"{Fore.RED}[Anti Error]: Kick-Permissions ({after.guild.name}){Fore.RESET}")

            if not before.permissions.administrator and after.permissions.administrator:
                try:
                    if punishment == 'kick':
                      await after.guild.kick(entry.user, reason="[refuge protection]\n・User Caught Giving Role Unsafe Permissions.")
                      await after.edit(permissions=1166401)
                      return
                    if punishment == 'ban':
                      await after.guild.ban(entry.user, reason="[refuge protection]\n・User Caught Giving Role Unsafe Permissions.")
                      await after.edit(permissions=1166401)
                      return
                except Exception as error:
                    if isinstance(error, discord.Forbidden):
                      return
                    else:
                      return print(f"{Fore.RED}[Anti Error]: Admin-Permissions ({after.guild.name}){Fore.RESET}")

            if entry.target.id == before.guild.id:
              if after.permissions.kick_members or after.permissions.ban_members or after.permissions.administrator or after.permissions.mention_everyone or after.permissions.manage_roles:
                try:
                  if punishment == 'kick':
                    await after.guild.kick(entry.user, reason="[refuge protection]\n・User Caught Giving Role Unsafe Permissions.")
                    await after.edit(permissions=1166401)
                    return
                  if punishment == 'ban':
                    await after.guild.ban(entry.user, reason="[refuge protection]\n・User Caught Giving Role Unsafe Permissions.")
                    await after.edit(permissions=1166401)
                    return
                except Exception as error:
                  if isinstance(error, discord.Forbidden):
                    return
                  else:
                    return print(f"{Fore.RED}[Anti Error]: Kick_Ban_Admin_Mention_Roles-Permissions ({after.guild.name}){Fore.RESET}")
            if entry.user.id not in whitelistedUsers or entry.user not in whitelistedUsers:   
              try:     
                if logschannel != None:
                  embed2 = discord.Embed(
                    title=f"[refuge logs] Permissions Granted On A Role. (unauthorized)", 
                    description=f"User caught giving roles dangerous permissions => `{entry.user.name}` \n<a:R_Arrow:767064076512919552> Action Taken: `{punishment}`",
                    colour=self.colour
                  )
                  return await logschannel.send(embed=embed2)
              except:
                pass
            return
        except Exception as error:
          if isinstance(error, discord.Forbidden):
            return
          else:
            return print(f"{Fore.RED}[Anti Error]: {error} | Anti-Permissions. ({after.guild.name}){Fore.RESET}") 

# anti member give role unsafe perms - still broken :(
#    @commands.Cog.listener()
#    async def on_member_update(self, before, after):
#      punishment = await db.find_one({ "guild_id": after.guild.id })["punishment"]
#      whitelistedUsers = await db.find_one({ "guild_id": after.guild.id })["user_whitelist"]
#      logschannelid = await db.find_one({ "guild_id": after.guild.id })["logs_channel"]
#      logschannel = self.client.get_channel(logschannelid)
#      guild = after.guild
#      try:
#        async for entry in guild.audit_logs(limit=1, after=datetime.datetime.now() - datetime.timedelta(seconds = 3)):
#          if entry.action == discord.AuditLogAction.member_role_update:
#            if len(entry.user.roles) != len(entry.user.roles):
#              if entry.user.id in whitelistedUsers or entry.user in whitelistedUsers:
#                if logschannel != None:
#                  embed = discord.Embed(
#                    title=f"[Refuge Logs]: Added Unsafe Roles to User. (authorized)", 
#                    description=f"Role: {entry.role.name} | `{entry.role.id}`\nUpdated by: {entry.user.name} | `{entry.user.id}`\nActions Taken: `None`",
#                    colour=self.colour
#                  )
#                  return await logschannel.send(embed=embed)
#              for role in after.roles:
#                if role not in before.roles:
#                  if role.permissions.administrator or role.permissions.manage_guild or role.permissions.kick_members or role.permissions.ban_members:
#                    await after.remove_roles(role)
#                  if punishment == 'kick':
#                    return await entry.user.kick(reason="[refuge protection]\n・Giving members unsafe roles.")
#                  if punishment == 'ban':
#                    return await entry.user.ban(reason="[refuge protection]\n・Giving members unsafe roles.")
#                  if logschannel != None:
#                    embed = discord.Embed(
#                      title=f"[Refuge Logs] Added Unsafe Roles to User. (unauthorized)", 
#                      description=f"Role: {entry.role.name} | `{entry.role.id}`\nUpdated by: {entry.user.name} | `{entry.user.id}`\nAction Taken: `{punishment}`",
#                      colour=self.colour
#                    )
#                  return await logschannel.send(embed=embed)
#      except Exception as error:
#        if isinstance(error, discord.Forbidden):
#          return
#        else:
#          return print(f"{Fore.RED}[Anti Error]: {error} | Anti-Unsafe-Role-Give. ({entry.guild.name}){Fore.RESET}") 

# anti vanity
    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
      data = await antitoggle.find_one({ "guild_id": after.id })
      if data["vanity_protect"] != "True":
        return
      if before.premium_tier == 3:
        data = await db.find_one({ "guild_id": after.id })
        punishment = data["punishment"]
        whitelistedUsers = data["user_whitelist"]
        logschannelid = data["logs_channel"]
        logschannel = self.client.get_channel(logschannelid)
        try:
          before_vanity = await before.vanity_invite()
          after_vanity = await after.vanity_invite()
          if before_vanity != after_vanity:
            async for entry in after.audit_logs(limit=1, after=datetime.datetime.now() - datetime.timedelta(seconds = 3), action=discord.AuditLogDiff.vanity_url_code):
              if entry.user.id in whitelistedUsers or entry.user in whitelistedUsers:
                if data["dm_logs"] == "True" and entry.user != after.owner:
                  await after.owner.send(f"<:r_alert:860644383535267850> This is a beta feature.\nA user has triggered my protection system: {entry.user} => No actions have been taken as they are whitelisted.")
                if logschannel != None:
                  embed = discord.Embed(
                    title=f"[refuge logs]: Vanity Changed. (authorized)", 
                    description=f"Vanity: {before_vanity} | {after_vanity}\nUpdated by: {entry.user.name} | `{entry.user.id}`\nActions Taken: `None`",
                  )
                  await logschannel.send(embed=embed)
                return
              if entry.target == before:
                try:
                  if punishment == 'kick':
                    await entry.user.kick(reason="[refuge protection]\n・Unauthorized user changing vanity.")
                    if logschannel != None:
                      embed2 = discord.Embed(
                        title=f"[refuge logs] Vanity Changed. (unauthorized)", 
                        description=f"Vanity: {before_vanity} | `{after_vanity}`\nUpdated by: {entry.user.name} | `{entry.user.id}`\nAction Taken: `{punishment}`",
                        colour=self.colour
                      )
                      await logschannel.send(embed=embed2)
                  if punishment == 'ban':
                    await entry.user.ban(reason="[refuge protection]\n・Unauthorized user changing vanity.")
                    if logschannel != None:
                      embed2 = discord.Embed(
                        title=f"[refuge logs] Vanity Changed. (unauthorized)", 
                        description=f"Vanity: {before_vanity} | `{after_vanity}`\nUpdated by: {entry.user.name} | `{entry.user.id}`\nAction Taken: `{punishment}`",
                        colour=self.colour
                      )
                      await logschannel.send(embed=embed2)
                  session.patch(f"https://discord.com/api/v9/guilds/{after.id}/vanity-url/{before_vanity}")
                except Exception as error:
                  if isinstance(error, discord.Forbidden):
                    return
                  else:
                    return print(f"{Fore.RED}[Anti Error]: Vanity Protection ({after.name}){Fore.RESET}")
        except Exception as error:
          if isinstance(error, discord.Forbidden):
            return
          else:
            return print(f"{Fore.RED}[Anti Error]: {error} | Anti-Vanity. ({after.name}){Fore.RESET}") 



def setup(client):
    client.add_cog(Anti(client))