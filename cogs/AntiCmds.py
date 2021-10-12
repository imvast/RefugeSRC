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


class AntiCmds(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.db = db
        self.colour = discord.Colour.random()
        print(f"{C.CYAN}[Status] Cog Loaded: AntiCmds" + C.RESET)


#def is_owner(self, ctx):
#    return ctx.message.author.id == int(os.environ.get('OWNERID'))
#def is_whitelisted(self, ctx):
#    return ctx.message.author.id in db.find_one({ "guild_id": ctx.guild.id })["user_whitelist"] or ctx.message.author.id == int(os.environ.get('OWNERID'))
#def is_server_owner(self, ctx):
#    return ctx.message.author.id == ctx.guild.owner.id or ctx.message.author.id == int(os.environ.get('OWNERID'))


    @commands.command(
      name='setup',
      description="Anti Feature | Fully Setup the Anti feature.",
      usage="setup"
    )
    @commands.has_permissions(administrator=True)
    @blacklist_check()
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def setup(self, ctx):
        """
        setup
        """
        logchannelid = self.db.find_one({'guild_id': ctx.guild.id})['logs_channel']
        await ctx.reply(embed=create_embed("<:r_warning:776595866558529576> New Setup Currently In Early Release.\n*Make sure to report any errors you recieve.*"))
        extras = self.db.find_one({'guild_id': ctx.guild.id})['prefix']
        starttime = time.perf_counter()
        embed = discord.Embed(
          title = "<:r_util:782064575361056808> Setting up refuge's Anti-Nuke:",
          colour=self.colour,
          description = "[<a:R_Loading:779124308819443732>] Checking permissions and hierarchy..."
        )
        embed.set_thumbnail(url=self.client.user.avatar_url)
        embed = await ctx.send(embed=embed)
        if ctx.guild.me.top_role in ctx.guild.roles[:-4:-1]:
          second_embed = discord.Embed(
            title = "<:r_util:782064575361056808> Setting up refuge's Anti-Nuke:",
            colour=self.colour,
            description=f"[<:r_yes:847976269122371595>] Checking permissions and hierarchy..."
          )
          second_embed.set_thumbnail(url=self.client.user.avatar_url)
          await embed.edit(embed=second_embed)
        else:
          second_embed = discord.Embed(
            title = "<:r_util:782064575361056808> Setting up refuge's Anti-Nuke:",
            colour=self.colour,
            description=f"[<:r_no:847976222793269250>] Checking permissions and hierarchy...\n\n**Please check my permissions and make sure my top role's placement is within the top 3 roles.**"
          )
          second_embed.set_thumbnail(url=self.client.user.avatar_url)
          return await embed.edit(embed=second_embed)
        third_embed = discord.Embed(
        title = "<:r_util:782064575361056808> Setting up refuge's Anti-Nuke:",
        colour=self.colour,
        description=f"[<:r_yes:847976269122371595>] Checking permissions and hierarchy...\n[<a:R_Loading:779124308819443732>] Checking for existing log channel..."
        )
        third_embed.set_thumbnail(url=self.client.user.avatar_url)
        await embed.edit(embed=third_embed)
        for channel in ctx.guild.channels:
          if channel.name == "refuge-logs":
            if logchannelid == 0:
              log_found = False
              await ctx.send(embed=create_error_embed("**Error**: A log channel was found but is not in the database. Resetting..."), delete_after=10)
              await channel.delete()
              break
            else:
              log_found = True
              break
          else:
            log_found = False
        if log_found == True:
            log_found_embed = discord.Embed(
              title = "<:r_util:782064575361056808> Setting up refuge's Anti-Nuke:",
              colour=self.colour,
              description=f"[<:r_yes:847976269122371595>] Checking permissions and hierarchy...\n[<:r_yes:847976269122371595>] Checking for existing log channel...\n"
            )
            log_found_embed.set_thumbnail(url=self.client.user.avatar_url)
            await embed.edit(embed=log_found_embed)
        elif log_found == False:
            log_notfound_embed1 = discord.Embed(
              title = "<:r_util:782064575361056808> Setting up refuge's Anti-Nuke:",
              colour=self.colour,
              description=f"[<:r_yes:847976269122371595>] Checking permissions and hierarchy...\n[<:r_no:847976222793269250>] Checking for existing log channel...\n<:r_rdarrow:864997826604826624>[<a:R_Loading:779124308819443732>] Creating log channel..."
            )
            log_notfound_embed1.set_thumbnail(url=self.client.user.avatar_url)
            await embed.edit(embed=log_notfound_embed1)
            channel = await ctx.guild.create_text_channel('refuge-logs')
            await channel.set_permissions(ctx.guild.default_role, send_messages=False, read_messages=False)
            self.db.update_one({'guild_id': ctx.guild.id}, {'$set': {'logs_channel': channel.id}})
            await channel.send(embed=create_embed("<:Icon_TextChannel:776616614224855040> This is now the logging channel where all the anti-nuke logs will be stored.\n<:r_warning:776595866558529576> To disable just delete the channel. (disable commands coming soon!)"))
            log_notfound_embed2 = discord.Embed(
              title = "<:r_util:782064575361056808> Setting up refuge's Anti-Nuke:",
              colour=self.colour,
              description=f"[<:r_yes:847976269122371595>] Checking permissions and hierarchy...\n[<:r_no:847976222793269250>] Checking for existing log channel...\n<:r_rdarrow:864997826604826624>[<:r_yes:847976269122371595>] Creating log channel..."
            )
            log_notfound_embed2.set_thumbnail(url=self.client.user.avatar_url)
            await embed.edit(embed=log_notfound_embed2)
        for role in ctx.guild.roles:
          if role.name.lower() == "muted":
            mute_found = True
            break
          else:
            mute_found = False
        if mute_found == False:
          if log_found == False:
            createmute_embed1 = discord.Embed(
              title = "<:r_util:782064575361056808> Setting up refuge's Anti-Nuke:",
              colour=self.colour,
              description=f"[<:r_yes:847976269122371595>] Checking permissions and hierarchy...\n[<:r_no:847976222793269250>] Checking for existing log channel...\n<:r_rdarrow:864997826604826624>[<:r_yes:847976269122371595>] Creating log channel...\n[<a:R_Loading:779124308819443732>] Checking for existing Mute role..."
            )
            createmute_embed1.set_thumbnail(url=self.client.user.avatar_url)
            await embed.edit(embed=createmute_embed1)
            muted = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
              await channel.set_permissions(muted, speak=False, send_messages=False, read_message_history=True, read_messages=True, connect=False)
            createmute_embed2 = discord.Embed(
              title = "<:r_util:782064575361056808> Setting up refuge's Anti-Nuke:",
              colour=self.colour,
              description=f"[<:r_yes:847976269122371595>] Checking permissions and hierarchy...\n[<:r_no:847976222793269250>] Checking for existing log channel...\n<:r_rdarrow:864997826604826624>[<:r_yes:847976269122371595>] Creating log channel...\n[<:r_no:847976222793269250>] Checking for existing Mute role...\n<:r_rdarrow:864997826604826624>[<:r_yes:847976269122371595>] Creating & Setting Up Mute Role...\n\nrefuge anti-nuke and moderation is one of the most reliable and safest discord bots out on discord. With refuge you can, stop raiders/nukers, and feel safe at all times with nobody to have the ability to ruin your server! For more information on refuge's anti-nuke system, use: `" + ' and '.join(extras) + "help anti`.\n\n<:r_check:780938741640200239> __**Whitelist:**__\nTo whitelist a user from refuge's protection system, you can use the command, `" + ' and '.join(extras) + f"whitelist @saiv`. But, be aware of, once a user is on refuge's whitelist __no__ actions will be taken against them and they will have the ability to ruin your server.\n\n<:r_check:780938741640200239> __**Logging:**__\nLogs for this server have been successfully setup in <#{logchannelid}>! To change where you would like the logging messages to be sent, use the command, `" + ' and '.join(extras) + "log #channel`"
            )
            createmute_embed2.set_thumbnail(url=self.client.user.avatar_url)
            await embed.edit(embed=createmute_embed2)
          if log_found == True: 
            createmute_embed3 = discord.Embed(
              title = "<:r_util:782064575361056808> Setting up refuge's Anti-Nuke:",
              colour=self.colour,
              description=f"[<:r_yes:847976269122371595>] Checking permissions and hierarchy...\n[<:r_yes:847976269122371595>] Checking for existing log channel...\n[<:r_no:847976222793269250>] Checking for existing Mute role...\n<:r_rdarrow:864997826604826624>[<a:R_Loading:779124308819443732>] Creating & Setting Up Mute Role..."
            )
            createmute_embed3.set_thumbnail(url=self.client.user.avatar_url)
            await embed.edit(embed=createmute_embed3)
            muted = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
              await channel.set_permissions(muted, speak=False, send_messages=False, read_message_history=True, read_messages=True, connect=False)
            createmute_embed4 = discord.Embed(
              title = "<:r_util:782064575361056808> Setting up refuge's Anti-Nuke:",
              colour=self.colour,
              description=f"[<:r_yes:847976269122371595>] Checking permissions and hierarchy...\n[<:r_yes:847976269122371595>] Checking for existing log channel...\n[<:r_no:847976222793269250>] Checking for existing Mute role...\n<:r_rdarrow:864997826604826624>[<:r_yes:847976269122371595>] Creating & Setting Up Mute Role...\n\nrefuge anti-nuke and moderation is one of the most reliable and safest discord bots out on discord. With refuge you can, stop raiders/nukers, and feel safe at all times with nobody to have the ability to ruin your server! For more information on refuge's anti-nuke system, use: `" + ' and '.join(extras) + "help anti`.\n\n<:r_check:780938741640200239> __**Whitelist:**__\nTo whitelist a user from refuge's protection system, you can use the command, `" + ' and '.join(extras) + f"whitelist @saiv`. But, be aware of, once a user is on refuge's whitelist __no__ actions will be taken against them and they will have the ability to ruin your server.\n\n<:r_check:780938741640200239> __**Logging:**__\nLogs for this server have been successfully setup in <#{logchannelid}>! To change where you would like the logging messages to be sent, use the command, `" + ' and '.join(extras) + "log #channel`"
            )
            createmute_embed4.set_thumbnail(url=self.client.user.avatar_url)
            await embed.edit(embed=createmute_embed4)
        if mute_found == True:
          if log_found == False:
            mutefound_embed1 = discord.Embed(
              title = "<:r_util:782064575361056808> Setting up refuge's Anti-Nuke:",
              colour=self.colour,
              description=f"[<:r_yes:847976269122371595>] Checking permissions and hierarchy...\n[<:r_no:847976222793269250>] Checking for existing log channel...\n<:r_rdarrow:864997826604826624>[<:r_yes:847976269122371595>] Creating log channel...\n[<a:R_Loading:779124308819443732>] Checking for existing Mute role..."
            )
            mutefound_embed1.set_thumbnail(url=self.client.user.avatar_url)
            await embed.edit(embed=mutefound_embed1)
            mutefound_embed2 = discord.Embed(
              title = "<:r_util:782064575361056808> Setting up refuge's Anti-Nuke:",
              colour=self.colour,
              description=f"[<:r_yes:847976269122371595>] Checking permissions and hierarchy...\n[<:r_no:847976222793269250>] Checking for existing log channel...\n<:r_rdarrow:864997826604826624>[<:r_yes:847976269122371595>] Creating log channel...\n[<:r_yes:847976269122371595>] Checking for existing Mute role...\n\nrefuge anti-nuke and moderation is one of the most reliable and safest discord bots out on discord. With refuge you can, stop raiders/nukers, and feel safe at all times with nobody to have the ability to ruin your server! For more information on refuge's anti-nuke system, use: `" + ' and '.join(extras) + "help anti`.\n\n<:r_check:780938741640200239> __**Whitelist:**__\nTo whitelist a user from refuge's protection system, you can use the command, `" + ' and '.join(extras) + f"whitelist @saiv`. But, be aware of, once a user is on refuge's whitelist __no__ actions will be taken against them and they will have the ability to ruin your server.\n\n<:r_check:780938741640200239> __**Logging:**__\nLogs for this server have been successfully setup in <#{logchannelid}>! To change where you would like the logging messages to be sent, use the command, `" + ' and '.join(extras) + "log #channel`"
            )
            mutefound_embed2.set_thumbnail(url=self.client.user.avatar_url)
            await embed.edit(embed=mutefound_embed2)
          if log_found == True: 
            createmute_embed3 = discord.Embed(
              title = "<:r_util:782064575361056808> Setting up refuge's Anti-Nuke:",
              colour=self.colour,
              description=f"[<:r_yes:847976269122371595>] Checking permissions and hierarchy...\n[<:r_yes:847976269122371595>] Checking for existing log channel...\n[<a:R_Loading:779124308819443732>] Checking for existing Mute role..."
            )
            createmute_embed3.set_thumbnail(url=self.client.user.avatar_url)
            await embed.edit(embed=createmute_embed3)
            mutefound_embed4 = discord.Embed(
              title = "<:r_util:782064575361056808> Setting up refuge's Anti-Nuke:",
              colour=self.colour,
              description=f"[<:r_yes:847976269122371595>] Checking permissions and hierarchy...\n[<:r_yes:847976269122371595>] Checking for existing log channel...\n[<:r_yes:847976269122371595>] Checking for existing Mute role...\n\nrefuge anti-nuke and moderation is one of the most reliable and safest discord bots out on discord. With refuge you can, stop raiders/nukers, and feel safe at all times with nobody to have the ability to ruin your server! For more information on refuge's anti-nuke system, use: `" + ' and '.join(extras) + "help anti`.\n\n<:r_check:780938741640200239> __**Whitelist:**__\nTo whitelist a user from refuge's protection system, you can use the command, `" + ' and '.join(extras) + f"whitelist @saiv`. But, be aware of, once a user is on refuge's whitelist __no__ actions will be taken against them and they will have the ability to ruin your server.\n\n<:r_check:780938741640200239> __**Logging:**__\nLogs for this server have been successfully setup in <#{logchannelid}>! To change where you would like the logging messages to be sent, use the command, `" + ' and '.join(extras) + "log #channel`"
            )
            mutefound_embed4.set_thumbnail(url=self.client.user.avatar_url)
            await embed.edit(embed=mutefound_embed4)
        endtime = time.perf_counter()
        await ctx.send(embed=create_embed(f"Setup completed in `{endtime - starttime:0.4f}` seconds."))


    @commands.command(
      name='punishment',
      description="Anti Feature | Setup the user punishment for Anti.",
      usage="punishment <ban/kick>"
    )
    @blacklist_check()
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def punishment(self, ctx, punishment = None):
      """
      punishment ban
      """
      if ctx.message.author.id == ctx.guild.owner.id:
        if punishment == None:
            embed = discord.Embed(title='refuge', colour=self.colour, description=f'**Please specify the guild punishment you want set.**')
            embed.set_thumbnail(url=self.client.user.avatar_url)
            await ctx.send(embed=embed)
        if punishment.lower() == 'ban':
            db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "punishment": "ban"}})
            embed = discord.Embed(title='refuge', colour=self.colour, description=f'<:r_hammer:860614861238960148> **Punishment updated!**\n**・User\'s will now be `banned` if suspicious activity is found within.**')
            embed.set_thumbnail(url=self.client.user.avatar_url)
            await ctx.send(embed=embed)
        elif punishment.lower() == 'kick':
            db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "punishment": "kick"}})
            embed = discord.Embed(title='refuge', colour=self.colour, description=f'<:r_hammer:860614861238960148> **Punishment updated!**\n**・User\'s will now be `kicked` if suspicious activity is found within.**')
            embed.set_thumbnail(url=self.client.user.avatar_url)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title='refuge', colour=self.colour, description=f'**Invalid Punishment.\n・ Punishments Are Currently: `ban` or `kick`!**')
            embed.set_thumbnail(url=self.client.user.avatar_url)
            await ctx.send(embed=embed)
      else:
        await ctx.send(embed=not_server_owner_msg())

    @commands.command(
      name='settings',
      description="Anti Feature | Returns Current Server Anti Settings.\nnote: still in beta; this command alone is 200+ lines 😫",
      usage="settings",
      aliases=['config']
    )
    @commands.has_permissions(administrator=True)
    @blacklist_check()
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def settings(self, ctx):
      # TYPES/HANDLERS #
      enabled_true = "<:enabled:845063898419429376>"
      enabled_false = "<:disabled:845063983396421662>"
      errtext = "Umm yeah wtf some bs error in the db just broke this command LMAO | dm saiv#3777 if you see this."
      # MAIN CHECKING #
      logchannelid = self.db.find_one({'guild_id': ctx.guild.id})['logs_channel']
      logcheck1 = self.client.get_channel(logchannelid)
      punishment = self.db.find_one({'guild_id': ctx.guild.id})['punishment']
      #-- limits
      banlimit = limits.find_one({'guild_id': ctx.guild.id})['bans_limit']
      kicklimit = limits.find_one({'guild_id': ctx.guild.id})['kicks_limit']
      roledel_limit = limits.find_one({'guild_id': ctx.guild.id})['role_delete_limit']
      chanadd_limit = limits.find_one({'guild_id': ctx.guild.id})['channel_delete_limit']
      #-- toggles
      ban_toggle = antitoggle.find_one({'guild_id': ctx.guild.id})['massban']
      kick_toggle = antitoggle.find_one({'guild_id': ctx.guild.id})['masskick']
      chanadd_toggle = antitoggle.find_one({'guild_id': ctx.guild.id})['channel_create']
      roleadd_toggle = antitoggle.find_one({'guild_id': ctx.guild.id})['role_create']
      webhook_toggle = antitoggle.find_one({'guild_id': ctx.guild.id})['webhook_ud']
      vanitysteal_toggle = antitoggle.find_one({'guild_id': ctx.guild.id})['vanity_protect']
      dmlog = db.find_one({'guild_id': ctx.guild.id})['dm_logs']
      if logcheck1 != None:
        logcheck = enabled_true
      else:
        logcheck = enabled_false
      premium = self.db.find_one({ "guild_id": ctx.guild.id })["premium"]
      if premium == "True":
        title = f"__refuge Premium Anti Settings__ ~ {ctx.guild.name}"
      else:
        title = f"__refuge Anti-Nuke Settings__ ~ {ctx.guild.name}"
      # TOGGLE CHECKS #
      if ban_toggle == "True": togglecheck_ban = enabled_true
      elif ban_toggle == "False": togglecheck_ban = enabled_false
      else: return await ctx.send(embed=create_error_embed(errtext))
      if kick_toggle == "True": togglecheck_kick = enabled_true
      elif kick_toggle == "False": togglecheck_kick = enabled_false
      else: return await ctx.send(embed=create_error_embed(errtext))
      if chanadd_toggle == "True": togglecheck_channels = enabled_true
      elif chanadd_toggle == "False": togglecheck_channels = enabled_false
      else: return await ctx.send(embed=create_error_embed(errtext))
      if roleadd_toggle == "True": togglecheck_roles = enabled_true
      elif roleadd_toggle == "False": togglecheck_roles = enabled_false
      else: return await ctx.send(embed=create_error_embed(errtext))
      if webhook_toggle == "True": togglecheck_webhook = enabled_true
      elif webhook_toggle == "False": togglecheck_webhook = enabled_false
      else: return await ctx.send(embed=create_error_embed(errtext))
      if vanitysteal_toggle == "True": togglecheck_vanity = enabled_true
      elif vanitysteal_toggle == "False": togglecheck_vanity = enabled_false
      else: return await ctx.send(embed=create_error_embed(errtext))
      if dmlog == "True": dmcheck = enabled_true
      elif dmlog == "False": dmcheck = enabled_false
      else: return await ctx.send(embed=create_error_embed(errtext))
      # VALUES #
      if logcheck == enabled_true:
        logval = f"・ Channel: <#{logchannelid}>\n・ DM: {dmcheck}"
      else:
        logval = f"{logcheck}"
      if togglecheck_ban == enabled_false:
        banval = f"{togglecheck_ban}"
      if togglecheck_ban == enabled_true:
        banval = f"・ Threshold: `{banlimit}`/`20s`\n・ Punishment: `{punishment}`"
      if togglecheck_kick == enabled_false:
        kickval = f"{togglecheck_kick}"
      if togglecheck_kick == enabled_true:
        kickval = f"・ Threshold: `{kicklimit}`/`20s`\n・ Punishment: `{punishment}`"
      if togglecheck_channels == enabled_false:
        chanaddval = f"{togglecheck_channels}"
      if togglecheck_channels == enabled_true:
        chanaddval = f"・ Threshold: `{chanadd_limit}`/`20s`\n・ Punishment: `{punishment}`"
      if togglecheck_roles == enabled_false:
        roledelval = f"{togglecheck_roles}"
      if togglecheck_roles == enabled_true:
        roledelval = f"・ Threshold: `{roledel_limit}`/`20s`\n・ Punishment: `{punishment}`"
      if ctx.guild.premium_tier == 3:
        if togglecheck_vanity == enabled_true:
          vanityval = f"・ Punishment: `{punishment}`"
        if togglecheck_vanity == enabled_false:
          vanityval = f"・ Enabled: {togglecheck_vanity}"
      else:
        togglecheck_vanity = enabled_false
        vanityval = f"・ Your server does not support the vanity setting."
      if togglecheck_webhook == enabled_false:
        webhookval = f"・ {togglecheck_webhook} Disabled"
      if togglecheck_webhook == enabled_true:
        webhookval = f"・ Punishment: `{punishment}`"

      # EMBED/MAIN MESSAGE #
      embed = discord.Embed(title=title, description="・ Individual `set punishment` is coming soon.\n・ Customizable thresholds are still being debated. (we apologize for the delay)", colour=self.colour)
      embed.add_field(
        name=f"Anti-Ban・{togglecheck_ban}",
        value=banval,
        inline=True
      )
      embed.add_field(
        name=f"Anti-Kick・{togglecheck_kick}",
        value=kickval,
        inline=True
      )
      embed.add_field(
        name=f"Anti-Bot・{enabled_true}",
        value=f"・ Punishment: `{punishment}`\n・ *Toggle Not Available*.",
        inline=True
      )
      embed.add_field(
        name=f"Anti-Roles・{togglecheck_roles}",
        value=roledelval,
        inline=True
      )
      embed.add_field(
        name=f"Anti-Permissions・{enabled_true}",
        value=f"・ Punishment: `{punishment}`\n・ *Toggle Not Available*.",
        inline=True
      )
      embed.add_field(
        name=f"Anti-Channels・{togglecheck_channels}",
        value=chanaddval,
        inline=True
      )
      embed.add_field(
        name=f"Anti-Webhook・{togglecheck_webhook}",
        value=webhookval,
        inline=True
      )
      embed.add_field(
        name=f"Anti-Vanity-Steal・{togglecheck_vanity}",
        value=vanityval,
        inline=True
      )
      #embed.add_field(
        #name=f"Anti-Link (unreleased)・{premanticheck}",
        #value=f"・ Allowed: `None`\n・ Punishment: `message-delete`",
        #inline=True
        #)
      #embed.add_field(
        #name=f"Anti-Spam (unreleased)・{premanticheck}",
        #value=f"・ Amount: `N/A`\n・ Punishment: `None`",
        #inline=True
      #)
      #embed.add_field(
        #name=f"Altdentifier (unreleased)・{premanticheck}",
        #value=f"・ Amount: `N/A`\n・ Punishment: `None`",
        #inline=True
      #)
      embed.add_field(
        name="Logging / Logs",
        value=logval
      )
      await ctx.send(embed=embed)


    @commands.command(
      name="whitelisted",
      description="Anti Feature | Returns list of whitelisted users.",
      usage="whitelisted",
      aliases=["wld", "trusted"]
    )
    @blacklist_check()
    #@commands.check(is_server_owner)
    async def whitelisted(self, ctx):
      if ctx.message.author.id == ctx.guild.owner.id:
        data = db.find_one({ "guild_id": ctx.guild.id })['user_whitelist']
        embed = discord.Embed(title=f"Whitelist for {ctx.guild.name}", description="\n")
        for i in data:
          if self.client.get_user(i) != None:
            if self.client.get_user(i) == ctx.guild.owner:
              embed.description += f"<a:crown:776616530368004116>・{self.client.get_user(i)} - {i}\n"
            if self.client.get_user(i) != ctx.guild.owner:
              if self.client.get_user(i).bot:
                embed.description += f"<:ClydeBot:776617480524136468>・{self.client.get_user(i)} - {i}\n"
              else:
                embed.description += f"<:users_logo:776597644410748938>・{self.client.get_user(i)} - {i}\n"
        await ctx.send(embed=embed)
      else:
        await ctx.send(embed=not_server_owner_msg())


    @commands.command(
      name='whitelist',
      description="Anti Feature | Add's mentioned user to trusted members. (adding whitelisting for roles soon)",
      usage="whitelist <user>",
      aliases=['wl', 'trust']
    )
    @blacklist_check()
    #@commands.check(is_server_owner)
    async def whitelist(self, ctx, *, user: discord.User):
      if ctx.message.author.id == ctx.guild.owner.id:
        if not isinstance(user, discord.User) or not user:
            return await ctx.reply(embed=create_error_embed("An invalid user was provided."))
        elif user.id in db.find_one({ "guild_id": ctx.guild.id })["user_whitelist"]:
            return await ctx.send(embed=create_error_embed(f"{user} is already whitelisted."))
        else:
            db.update_one({ "guild_id": ctx.guild.id }, { "$push": { "user_whitelist": user.id }})
            return await ctx.send(embed=create_embed(f"・ `{user}` is now whitelisted in this server."))
      else:
        return await ctx.send(embed=not_server_owner_msg())


    @commands.command(
      name='unwhitelist',
      description="Anti Feature | Remove's mentioned user from trusted/whitelisted list.",
      usage="unwhitelist <user>",
      aliases=["dewhitelist", "dwl", "untrust", "uwl", "unwl"]
    )
    @blacklist_check()
    async def unwhitelist(self, ctx, *, user: discord.User):
      if ctx.message.author.id == ctx.guild.owner.id:
        if not isinstance(user, discord.User) or not user:
            return await ctx.reply(embed=create_error_embed("An invalid user was provided."))
        elif user.id not in db.find_one({ "guild_id": ctx.guild.id })["user_whitelist"]:
            return await ctx.send(embed=create_error_embed(f"{user} is not whitelisted."))
        elif user.id == ctx.guild.owner.id:
          return await ctx.send(embed=create_error_embed("The server owner cannot be unwhitelisted."))
        else:
            db.update_one({ "guild_id": ctx.guild.id }, { "$pull": { "user_whitelist": user.id }})
            await ctx.send(embed=create_embed(f"・ `{user}` is no longer whitelisted in this server."))
      else:
        await ctx.send(embed=not_server_owner_msg())


    @commands.command(
      name="unbanall",
      description="Anti Feature | Removes all bans in the current server.",
      usage="unbanall",
      aliases=["massunban", "purgebans", "clearbans"]
    )
    @blacklist_check()
    @commands.has_permissions(ban_members=True)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def unbanall(self, ctx):
        if not ctx.message.guild:
            return
        else:          
            tic = time.perf_counter()
            banlist = await ctx.guild.bans()
            members = [str(f'{users.user} - {users.user.id}') for users in banlist]
            ping = float(f'0.{int(self.client.latency * 1000)}') / 3
            est_time = round(len(members) * ping)
            txt = await ctx.send(embed=create_embed(f'・ Attempting to unban {len(members)} members... \n・ Estimated time until finished: {est_time} second(s).'))
            for users in banlist:
                try:
                    await ctx.guild.unban(user=users.user)
                except:
                    pass    
            toc = time.perf_counter()
            if len(members) == 0:
                await txt.edit(embed=create_error_embed("Nobody is banned. Therefore, I cannot unban anyone."))
                return

            per_page = 15 
            pages = math.ceil(len(members) / per_page)
            cur_page = 1
            chunk = members[:per_page]
            linebreak = "\n"
            
            em = discord.Embed(title=f"{len(members)} Users unbanned:", description=f"{linebreak.join(chunk)}", colour=self.colour)
            em.set_footer(text=f"Page {cur_page}/{pages}:")            
            message = await ctx.send(f"Took `{round(toc - tic)}` second(s) to unban `{len(members)}` members", embed=em)
            reaction = await message.add_reaction("<a:L_Arrow:767064087367647242>")
            reaction = await message.add_reaction("<a:R_Arrow:767064076512919552>")
            user = ctx.author
            active = True

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["<a:R_Arrow:767064076512919552>", "<a:L_Arrow:767064087367647242>"]

            while active:
                try:
                    reaction, user = await self.client.wait_for("reaction_add", timeout=60, check=check)
                
                    if str(reaction.emoji) == "<a:R_Arrow:767064076512919552>" and cur_page != pages:
                        cur_page += 1
                        if cur_page != pages:
                            chunk = members[(cur_page-1)*per_page:cur_page*per_page]
                        else:
                            chunk = members[(cur_page-1)*per_page:]
                        e = discord.Embed(title=f"{len(members)} Users unbanned:", description=f"{linebreak.join(chunk)}", colour=self.colour)
                        e.set_footer(text=f"Page {cur_page}/{pages}:")
                        await message.edit(embed=e)
                        await message.remove_reaction(reaction, user)
                    elif str(reaction.emoji) == "<a:L_Arrow:767064087367647242>" and cur_page > 1:
                        cur_page -= 1
                        chunk = members[(cur_page-1)*per_page:cur_page*per_page]
                        e = discord.Embed(title=f"{len(members)} Users unbanned:", description=f"{linebreak.join(chunk)}", colour=self.colour)
                        e.set_footer(text=f"Page {cur_page}/{pages}:")
                        await message.edit(embed=e)
                        await message.remove_reaction(reaction, user)
                except asyncio.TimeoutError:
                    await message.remove_reaction(reaction, user)
                    await message.remove_reaction(reaction, self.client.user)
                    await message.remove_reaction(reaction, user)
                    await message.remove_reaction(reaction, self.client.user)
                    active = False

    @commands.command(
      name="logchannel",
      description="Set logging channel for Anti-Nuke.",
      usage="logchannel <#channel>",
      aliases = ["log", "logchan", "logs", "logschannel"]
    )
    @commands.cooldown(1, 30, type=commands.BucketType.guild)
    @blacklist_check()
    async def logchannel(self, ctx, channel: discord.TextChannel = None):
      if ctx.author != ctx.guild.owner:
        return await ctx.reply(embed=not_server_owner_msg())
      if channel == None:
          channel = ctx.channel
          db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "logs_channel": ctx.channel.id }})
          await ctx.send(embed=create_embed(f'Updated Logs Channel to: {channel.mention}'))
          await channel.send(embed=create_embed("<:Icon_TextChannel:776616614224855040> This is now the logging channel where all the anti-nuke logs will be stored.\n<:r_warning:776595866558529576> To disable just delete the channel. (disable commands coming soon!)"))
      else:
          db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "logs_channel": channel.id }})
          await ctx.send(embed=create_embed(f'Updated Logs Channel to: {channel.mention}'))
          await channel.send(embed=create_embed("<:Icon_TextChannel:776616614224855040> This is now the logging channel where all the anti-nuke logs will be stored.\n<:r_warning:776595866558529576> To disable just delete the channel. (disable commands coming soon!)"))


    @commands.command(
      name="dmlogs",
      description="Enable/Disable DM owner logs.",
      usage="dmlogs <True/False>",
      aliases = ["dmlog"]
    )
    @blacklist_check()
    async def dmlogs(self, ctx, txt = None):
      if not ctx.author == ctx.guild.owner:
        return await ctx.reply(embed=not_server_owner_msg())
      extras = self.db.find_one({ "guild_id": ctx.guild.id })['prefix']
      if txt == None:
        if self.db.find_one({ "guild_id": ctx.guild.id })["dm_logs"] == "True":
          return await ctx.send(embed=create_error_embed('**Please specify `<True/False>`**\n**Example: `' + ' and '.join(extras) + 'dmlog True`**\n———————————————\nCurrent : **Enabled**'))
        if self.db.find_one({ "guild_id": ctx.guild.id })["dm_logs"] == "False":
          return await ctx.send(embed=create_error_embed('**Please specify `<True/False>`**\n**Example: `' + ' and '.join(extras) + 'dmlog True`**\n———————————————\nCurrent : **Disabled**'))
      if txt.lower() in ("true", "on", "enable"):
          self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "dm_logs": "True" }})
          return await ctx.send(embed=create_embed(f'・ Enabled DM Owner Logs.'))
      if txt.lower() in ("false", "off", "disable"):
          self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "dm_logs": "False" }})
          return await ctx.send(embed=create_embed(f'・ Disabled DM Owner Logs.'))
            


def setup(client):
    client.add_cog(AntiCmds(client))