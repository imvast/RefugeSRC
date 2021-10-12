# Imports
import discord, time, pymongo, os, datetime, random
from colorama import Fore as C
from settings import *
from discord.ext import commands
from discord_components import *

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
    

class Information(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.db = db
        self.messages = {}
        self.colour = discord.Colour.random()
        print(f"{C.CYAN}[Status] Cog Loaded: Information" + C.RESET)
    

    @commands.Cog.listener()
    async def on_message_delete(self, message): 
      if message.guild is None: 
          return
      if message.author.bot: 
          return
      if not message.content: 
          return 
      self.messages[message.channel.id] = message


    @commands.command(
        name="invite",
        description="Sends the bot's important links.",
        usage="invite",
        aliases=["inv", "support", "supportserver", "links", "docs", "upvote"]
    )
    @blacklist_check()
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def invite(self, ctx):
        """
        invite
        """
        embed = discord.Embed(
        title = "<:NVLink:776617844213153833> refuge's links",
        colour=self.colour,
        description = "[__**Bot Invite**__](https://discord.com/oauth2/authorize?client_id=771568117180268584&permissions=8&scope=bot%20applications.commands)\n[__**Support Server**__](https://discord.gg/D4vpbknawK)\n[__**Docs**__](https://docs.refugebot.xyz)\n[__**Upvote**__](https://top.gg/bot/771568117180268584/vote)\n"#[__**Patreon**__](Coming Soon)"
        )
        embed.set_thumbnail(url=self.client.user.avatar_url)
        message = await ctx.send(embed=embed)
        await message.add_reaction("<:NVLink:776617844213153833>")

    @commands.command(
        name="updateinfo",
        description="Returns important updates list.",
        usage="updateinfo",
        aliases=["ud-info", "udinfo", "updates"]
    )
    @blacklist_check()
    @commands.cooldown(1, 7, commands.BucketType.channel)
    async def updateinfo(self, ctx):
        """
        updateinfo
        """
        embed = discord.Embed(
        title = "__Important Updates__",
        colour=self.colour,
        description = "**-1.4.5** | **7-20-21**\n```・ Basically, redesigned everything.\n(some changes were small and others were big. either way, you will most likely notice.)```\n**-1.4.0** | **7-18-21**\n```[Made too many fixes to add here, so heres some of the major changes]\n\n・ Gave a little more change to some of the UIs\n・ Fixed an error with logs being spammed after actions.\n\n・ WIP: Making AntiNuke Reaction Speeds Faster; Giving the help command a little more modernization.```\n**-1.2.6** | **7-13-21**\n```・ Revamped Settings/Config Command.\n・ Fixed logs and working on redesign.```\n**-1.2.0** | **7-12-21**\n```・ Updated host.\n・ Made the best Anti-Ban\n・ Finished DM Logs.\n・ Working on design.```\n**-1.0.0** | **7-4-21**<:r_empty:863922473362522134><:r_empty:863922473362522134><:r_empty:863922473362522134><:r_empty:863922473362522134> |<:r_empty:863922473362522134>**-0.0.1b1** | **6-24-21**\n```・ Public launch.   |  ・ Beta launch.```"
        )
        embed.set_footer(text=f"Current Version: {os.environ.get('BOT_VERSION')} • July 18, 2021")
        embed.set_thumbnail(url=self.client.user.avatar_url)
        message = await ctx.send(embed=embed)
        await message.add_reaction("<:r_ud:856025701777539143>")

    @commands.command(
        name="ping",
        description="Returns all latencys for the bot.",
        usage="ping",
        aliases=["latency"]
    )
    @blacklist_check()
    @commands.cooldown(1, 7, commands.BucketType.channel)
    async def ping(self, ctx):
        """
        ping
        """
        latency = f"{int(self.client.latency * 1000)}ms."
        before = time.monotonic()
        msg = await ctx.send(embed=create_invis_embed("Loading..."))
        msgping = (time.monotonic() - before) * 1000
        embed2 = discord.Embed(
        colour=self.colour,
        description = f"**Client**\n```{latency}```\n**Message**\n```{int(msgping)}ms.```"
        )
        await msg.edit(embed=embed2)

    @commands.command(
        name="credits",
        description="Returns bot credits.",
        usage="credits",
        aliases=["creds"]
    )
    @blacklist_check()
    @commands.cooldown(1, 7, commands.BucketType.channel)
    async def credits(self, ctx):
        """
        credits
        """
        embed2 = discord.Embed(
        colour=self.colour,
        title="<a:r_exclamation:849496504695390228> Official Credits",
        description = f"refuge's official team. If anyone that isn't listed below claims to be a creator of refuge, they are 100% lying and should not be trusted.\n\n**__saiv#3777__** | `750507937746649159`\nPosition: Developer\nInfo: All around scripted refuge and hosting the bot.\n\n**__jays#0001__** | `263079024484417536`\nPosition: Owner\nInfo: God promoter and helped out on some of the scripting."
        )
        await ctx.send(embed=embed2)

    start_time = time.time()
    @commands.command(
        name="info",
        description="Shows information about the bot",
        usage="info",
        aliases=['information', 'about', 'botinfo', 'refuge']
    )
    @blacklist_check()
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def info(self, ctx):
      """
      info
      """
      # variables
      dpyversion = discord.__version__
      difference = int(round(time.time() - self.start_time))
      uptime_txt = str(datetime.timedelta(seconds=difference))
      latency = f"{int(self.client.latency * 1000)}ms."
      before = time.monotonic()
      extras = self.db.find_one({'guild_id': ctx.guild.id})['prefix']
      dbping = f"{round(time.monotonic() - before) * 1000}ms."
      # embed/message
      embed=discord.Embed(
        title="<a:x_Pin:776513817281691659> refuge bot info", 
        url="https://discord.com/oauth2/authorize?client_id=771568117180268584&permissions=8&scope=bot%20applications.commands", 
        icon_url=self.client.user.avatar_url, 
        colour=self.colour,
        timestamp=ctx.message.created_at
      )
      embed.set_footer(text=f"Requested by: {ctx.author}")
      embed.set_thumbnail(url=self.client.user.avatar_url)
      embed.add_field(
        name="<a:sparkles:857831750494715956> refuge",
        value=f"```cpp\nCreators  : {self.client.get_user(750507937746649159)}, {self.client.get_user(263079024484417536)}\nServers   : {len(self.client.guilds)}\nUsers     : {len(set(self.client.get_all_members()))}\nCommands  : {len(self.client.commands)}\nUptime    : {uptime_txt}```",
        inline=False
      )
      embed.add_field(
        name="<a:r_infinity:782450983711014983> Versions",
        value=f"```cpp\nrefuge    : {os.environ.get('BOT_VERSION')}\nDiscordPY : {dpyversion}\nPython    : 3.8.5```",
        inline=False
      )
      embed.add_field(
        name="<a:typingstatus:860907762744688710> Latency",
        value=f"```cpp\nClient    : {latency}\nMessage   : Loading...\nDatabase  : {dbping}```"
      )
      embed.add_field(
        name="❓ Prefixes",
        value=f"```asciidoc\n- " + ' and '.join(extras) + f"\n- refuge\n- {self.client.user.mention}```",
        inline=False
      )
      try:
        before = time.monotonic()
        msg = await ctx.send(embed=embed, components=[[Button(style=ButtonStyle.URL, label="Invite", url=f"https://discord.com/oauth2/authorize?client_id=771568117180268584&permissions=8&scope=bot%20applications.commands"), Button(style=ButtonStyle.URL, label="Support", url=f"https://discord.gg/polls"), Button(style=ButtonStyle.URL, label="Upvote", url=f"https://discordbotlist.com/bots/refuge/upvote")]])
        msgping = (time.monotonic() - before) * 1000
        await msg.add_reaction("<a:hearts_black:770076912541237249>")
      except Exception as e:
          return print(e)
      emb2=discord.Embed(
        title="<a:x_Pin:776513817281691659> refuge bot info", 
        url="https://discord.com/oauth2/authorize?client_id=771568117180268584&permissions=8&scope=bot%20applications.commands", 
        icon_url=self.client.user.avatar_url, 
        colour=self.colour,
        timestamp=ctx.message.created_at
        )
      emb2.set_footer(text=f"Requested by: {ctx.author}")
      emb2.set_thumbnail(url=self.client.user.avatar_url)
      emb2.add_field(
        name="<a:sparkles:857831750494715956> refuge",
        value=f"```cpp\nCreators  : {self.client.get_user(750507937746649159)}, {self.client.get_user(263079024484417536)}\nServers   : {len(self.client.guilds)}\nUsers     : {len(set(self.client.get_all_members()))}\nCommands  : {len(self.client.commands)}\nUptime    : {uptime_txt}```",
        inline=False
      )
      emb2.add_field(
        name="<a:r_infinity:782450983711014983> Versions",
        value=f"```cpp\nrefuge    : {os.environ.get('BOT_VERSION')}\nDiscordPY : {dpyversion}\nPython    : 3.8.5```",
        inline=False
      )
      emb2.add_field(
        name="<a:typingstatus:860907762744688710> Latency",
        value=f"```cpp\nClient    : {latency}\nMessage   : {int(msgping)}ms.\nDatabase  : {dbping}```"
      )
      emb2.add_field(
        name="❓ Prefixes",
        value=f"```asciidoc\n- " + ' and '.join(extras) + f"\n- refuge\n- {self.client.user.mention}```",
        inline=False
      )
      await msg.edit(embed=emb2, components=[[Button(style=ButtonStyle.URL, label="Invite", url=f"https://discord.com/oauth2/authorize?client_id=771568117180268584&permissions=8&scope=bot%20applications.commands"), Button(style=ButtonStyle.URL, label="Support", url=f"https://discord.gg/polls"), Button(style=ButtonStyle.URL, label="Upvote", url=f"https://discordbotlist.com/bots/refuge/upvote")]])


    @commands.command(
        name='snipe',
        description='Sends most recent deleted message.',
        usage="snipe",
        aliases=["s"]
    )
    @commands.cooldown(1, 3, commands.BucketType.channel)
    async def snipe(self, ctx): 
        """
        snipe
        """
        message = self.messages.get(ctx.channel.id)
        if message is None: 
            await ctx.send(embed=create_error_embed('I couldn\'t find anything to snipe.'))
        else:
            embed = discord.Embed(colour=self.colour, description=f"{message.content}", timestamp=message.created_at)
            embed.set_author(name=f"{str(message.author)}", icon_url=message.author.avatar_url)
            await ctx.send(embed=embed)


    @commands.command(
        name='whois',
        aliases=['userinfo', 'profile'],
        description='Displays info about the specified user.',
        usage="whois [user]"
    )
    @commands.cooldown(1, 5, commands.BucketType.channel)
    @blacklist_check()
    async def whois(self, ctx, member: discord.Member = None):
        """
        whois @saiv
        """
        if not member:  # if member is no mentioned
            member = ctx.message.author  # set member as the author
        roles = [role for role in member.roles]
        status = ""
        if member.status == discord.Status.dnd:
            status = "DND"
        elif member.status == discord.Status.idle:
            status = "IDLE"
        elif member.status == discord.Status.online:
            status = "ONLINE"
        elif member.status == discord.Status.offline:
            status = "OFFLINE"
        embed = discord.Embed(colour=ctx.author.color, timestamp=ctx.message.created_at)
        embed.set_author(name=f"{member} ・ {status}")
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=f"Requested by {ctx.author}")
        embed.add_field(name="Display Name", value=member.display_name)
        embed.add_field(name="ID", value=member.id)
        embed.add_field(name="<:r_plus:860643076300734496> Creation Date", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
        embed.add_field(name="<:r_join:860642891452645397> Joined Date", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
        embed.add_field(name="<:r_role:860643526093438986> Roles", value="".join([role.mention for role in roles]))
        embed.add_field(name="🔝 Highest Role", value=member.top_role.mention)
        embed.add_field(name="<a:r_booster:860643350041722890> Boosting", value=member.premium_since)
        await ctx.send(embed=embed, components=[Button(style=ButtonStyle.URL, label="Avatar", url=f"{member.avatar_url}")])


    @commands.command(
        name='serverinfo',
        description='Displays the server info',
        usage="serverinfo",
        aliases=["si", "guildinfo"]
    )
    @commands.cooldown(1, 5, commands.BucketType.channel)
    @blacklist_check()
    async def serverinfo(self, ctx):
        """
        serverinfo
        """
        guild = ctx.message.guild
        online = len([member.status for member in guild.members
                      if member.status == discord.Status.online or
                      member.status == discord.Status.idle or member.status == discord.Status.do_not_disturb])
        total_users = len(guild.members)
        total_bots = len([member for member in guild.members if member.bot == True])
        total_humans = total_users - total_bots
        text_channels = len(ctx.guild.text_channels)
        voice_channels = len(ctx.guild.voice_channels)
        passed = (ctx.message.created_at - guild.created_at).days
        created_at = ("Created on {}.".format(guild.created_at.strftime("`%d %b %Y` at `%H:%M`"), passed))
        if ctx.author.id in self.client.owner_ids:
            import aiohttp
            headers={"Authorization": f"Bot {os.environ.get('BOT_TOKEN')}"}
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(f'https://discord.com/api/v9/guilds/{guild.id}', headers=headers) as resp:
                    await ctx.send(embed=create_invis_embed(await resp.text()), delete_after=15)
        embed = discord.Embed(description=created_at, colour=self.colour,)
        embed.add_field(name="<a:crown:776616530368004116> **Owner**", value=str(guild.owner), inline=True)
        embed.add_field(name="<a:r_globe:862827224432508938> **Region**", value=str(guild.region), inline=True)
        embed.add_field(name="<a:boosts:776622883564290078> **Boosts**", value=guild.premium_subscription_count)
        embed.add_field(name="🏷 **Roles**", value=len(guild.roles), inline=True)
        embed.add_field(name="<:r_shrug:860641665986985995> Emojis", value=len(guild.emojis), inline=True)
        embed.add_field(name="<:1618_users_logo:776597644410748938> **Members**", value="<:online:857840298196729917> {} / {}\n🧍 {}\n<:ClydeBot:776617480524136468> {}".format(online, total_users, total_humans, total_bots), inline=True)
        embed.add_field(name="➕ **Channels**", value="<:DE_IconTextChannel:776616614224855040> {}\n<:vc:776617624448139294> {}".format(text_channels, voice_channels), inline=True)
        embed.set_footer(text=f"Server ID: {str(guild.id)}")
        
        if guild.icon_url:
            embed.set_author(name=guild.name, url=guild.icon_url)
            embed.set_thumbnail(url=guild.icon_url)
            await ctx.send(embed=embed, components=[Button(style=ButtonStyle.URL, label="Icon", url=f"{guild.icon_url}")])
        else:
            embed.set_author(name=guild.name)
            await ctx.send(embed=embed)
    

    # Error handlers

    @serverinfo.error
    async def serverinfo_error(self, ctx, error):
        await ctx.send(
            embed=create_error_embed(
                f"There was an error while attempting to get the server info."
            )
        )
        
    @whois.error
    async def whois_error(self, ctx, error):
        await ctx.send(
            embed=create_error_embed(
                f"Failed to get info on that user."
            )
        )



def setup(client):
    client.add_cog(Information(client))
