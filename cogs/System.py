# Imports
import discord, os, math, pymongo, asyncio
from settings import *
from colorama import Fore
from discord.ext import commands, tasks
from discord_webhook import DiscordWebhook, DiscordEmbed

# Connect to MongoDB
mongoClient = pymongo.MongoClient(os.environ.get('BOT_DB'))
db = mongoClient.get_database("refuge").get_collection("server-data")
db2 = mongoClient['refuge']
antitoggle = db2['antitoggle']
blacklist = db2['blacklist']
gprefix = db['prefix']
limits = db2['limits']


class System(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.db = db
        self.colour = discord.Colour.random()
        print(f"{Fore.CYAN}[Status] Cog Loaded: System" + Fore.RESET)
        
    @tasks.loop(minutes=3)
    async def clean_mods(self):
        await self.client.wait_until_ready()
        if self.abusewatch != {}:
          self.abusewatch = {}
          print(Fore.LIGHTMAGENTA_EX + "[Status] Cleared Abuse Watch." + Fore.RESET)

    # Commands
    @commands.command(
        name='reload',
        description='Owner Only | Reload a cog',
        usage='reload <cog name>'
    )
    @commands.is_owner()
    async def reload(self, ctx, extension):
        await ctx.message.delete()
        if extension.lower() == "system":
            return await ctx.reply("System.py can not be reloaded due to a ridiculous error that will occur afer doing so.")
        self.client.reload_extension(f'cogs.{extension}')
        print(f"[Status] Reloaded Cog: {extension}")
        await ctx.send(
            embed=create_embed(
                f"**{extension}** has been reloaded"
            ),
            delete_after=10
        )

    @commands.command(
        name='load',
        description='Owner Only | Load a cog',
        usage='load <cog name>'
    )
    @commands.is_owner()
    async def load(self, ctx, extension):
        await ctx.message.delete()
        self.client.load_extension(f'cogs.{extension}')
        print(f'[Status] Cog {extension} loaded successfully')
        await ctx.send(
            embed=create_embed(
                f"Cog **{extension}** loaded successfully"
            ),
            delete_after=10
        )

    @commands.command(
        name='unload',
        description='Owner Only | Unload a cog',
        usage='unload <cog name>'
    )
    @commands.is_owner()
    async def unload(self, ctx, extension):
        await ctx.message.delete()
        if extension.lower() == "system":
            return await ctx.reply("System.py can not be unloaded due to a ridiculous error that will occur afer doing so.")
        self.client.unload_extension(f'cogs.{extension}')
        print(f'[Status] Cog {extension} unloaded successfully')
        await ctx.send(
            embed=create_embed(
                f"Cog **{extension}** unloaded successfully"
            ),
            delete_after=10
        )


    @commands.command(
        name='sync',
        description='Owner Only | Sync\'s all cogs with latest version and publishes recent release to database.',
        usage='sync'
    )
    @commands.is_owner()
    async def sync(self, ctx):
        embed = discord.Embed(colour=self.colour)
        embed.add_field(name="<:r_dia:781221752163795014> Cogs", value="```cpp\nSyncing...```", inline = False)
        m = await ctx.reply(embed=embed)
        cogs=0
        try:
          for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and not filename.startswith('System'):
              self.client.reload_extension(f'cogs.{filename[:-3]}')
              cogs += 1
          posem = discord.Embed(colour=self.colour)
          posem.add_field(name="<:r_dia:781221752163795014> Cogs", value=f"```cpp\nSynced {cogs} cogs Successfully!```", inline = False)
          await m.edit(embed=posem)
        except:
            failem = discord.Embed(colour=self.colour)
            failem.add_field(name="<:r_dia:781221752163795014> Cogs", value=f"```cpp\nFailed to sync all cogs. Check console for error.```", inline = False)
            await m.edit(embed=failem)


    @commands.command(
        name='getserver',
        description='Owner Only | Gets info on the given server id.',
        usage='getserver <guild_id>',
        aliases=["getguild"]
    )
    @commands.is_owner()
    async def getserver(self, ctx, id: int):
        output = ''
        guild = self.client.get_guild(id)
        if not guild:
            return await ctx.send("Unkown Guild ID. This is likely caused by me not being in the specified guild id.")
        gn = guild.name
        gi = str(guild.id)
        gm = str(len(guild.members))
        go = str(guild.owner)
        output += f'Name: `{gn}`\nID: `{gi}`\nMembers: `{gm}`\nOwner: `{go}`\nInvite: `fetching...`'
        embed = discord.Embed(
            colour=self.colour,
            title=f'Guild Info For ID: {id}',
            description=output,
            timestamp=ctx.message.created_at
        )
        await ctx.send(embed=embed)

    @commands.command(
        name='getuser',
        description='Owner Only | Gets info on the given user id.',
        usage='getuser <userid>'
    )
    @commands.is_owner()
    async def getuser(self, ctx, id: int):
        output = ''
        user = self.client.get_user(id)
        if not user:
            return await ctx.send("Unkown User ID. This is likely caused by me not having any mutuals with the given user.")
        un = user.name
        ui = str(user.id)
        ug = ''
        ugc = 0
        guilds = self.client.guilds
        for guild in guilds:
            if guild.owner.id == id:
                ug += f"`{guild.name}`\n"
                ugc += 1
        if ug=='': ug="**None.**"
        output += f'Name: `{un}`\nID: `{ui}`\nServers: ({ugc})\n{ug}'
        embed = discord.Embed(
            colour=self.colour,
            title=f'Private User Info For ID: {id}',
            description=output,
            timestamp=ctx.message.created_at
        )
        await ctx.send(embed=embed)

    @commands.command(
        name='servers',
        description='Owner Only | List the servers that the bot is in',
        usage='servers',
        aliases=["serverlist"]
    )
    @commands.is_owner()
    async def servers(self, ctx, page: int = 1):
        output = ''
        guilds = self.client.guilds
        pages = math.ceil(len(guilds)/15)
        if 1 <= page <= pages:
            counter = 1+(page-1)*15
            for guild in guilds[(page-1)*15:page*15]:
                gn = guild.name
                gi = str(guild.id)
                gm = str(len(guild.members))
                go = str(guild.owner)
                output += f'**{counter}.** `{gn}` **|** `{gi}` **|** `{gm}` **|** `{go}`\n'
                counter += 1
            embed = discord.Embed(
                colour=self.colour,
                description=output,
                title='__**Server List**__',
                timestamp=ctx.message.created_at
            )
            embed.set_footer(
                text=f'Page {page} of {pages}'
            )
            msg = await ctx.send(
                embed=embed
            )
            await msg.add_reaction("<a:L_Arrow:767064087367647242>")
            await msg.add_reaction("<a:R_Arrow:767064076512919552>")
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["<a:R_Arrow:767064076512919552>", "<a:L_Arrow:767064087367647242>"]
            while True:
              try:
                reaction, user = await self.client.wait_for("reaction_add", timeout=60, check=check)
                if str(reaction.emoji) == "<a:L_Arrow:767064087367647242>":
                  page += 1
                elif str(reaction.emoji) == "<a:R_Arrow:767064076512919552>":
                  page -= 1
              except asyncio.TimeoutError:
                await msg.remove_reaction(reaction, ctx.author)
                await msg.remove_reaction(reaction, ctx.author)
                await msg.remove_reaction(reaction, self.client.user)
                await msg.remove_reaction(reaction, self.client.user)
        else:
            await ctx.send(
                embed=create_embed(
                    'Invalid Page Number.'
                ),
                delete_after=10
            )


    @commands.command(
        name='leaveserver',
        description='Owner Only | Leave the server of your choice',
        usage='leaveserver <number on list>'
    )
    @commands.is_owner()
    async def leaveserver(self, ctx, pos: int):
        guilds = self.client.guilds
        guild = guilds[pos-1]
        await guild.leave()
        await ctx.send(
            embed=create_embed(
                f'Left {guild.name}'
            )
        )

    @commands.command(
        name='blacklist',
        description='Owner Only | Blacklist users from using the bot',
        usage='blacklist <userid>'
    )
    @commands.is_owner()
    async def blacklist(self, ctx, userid: int, *, reason=None):
        if blacklist.find_one({'user_id': userid}):
            await ctx.send(
                embed=create_embed(
                    'User ID already blacklisted.'
                )
            )
        else:
            if self.client.get_user(userid) != None:
                blacklist.insert_one({'user_id': userid})
                await ctx.send(
                    embed=create_embed(
                        f'User, <@{userid}> is now blacklisted.'
                    )
                )
                user = self.client.get_user(userid)
                await user.send(embed=create_embed(f'You have been blacklisted from refuge.\nHeat Level: `2`\nReason: `{reason}`'))
            else:
                await ctx.send(
                    embed=create_embed(
                        'Unknown User ID. Please make sure that user is in a server that I am in!'
                    ),
                    delete_after=30
                )

    @commands.command(
        name='showblacklist',
        description='Owner Only | List of all blacklisted users.',
        usage='showblacklist <page>'
    )
    @commands.is_owner()
    async def showblacklist(self, ctx, page: int = 1):
        output = ''
        blacklisted = blacklist.find()
        pages = math.ceil(blacklisted.count()/10)
        if 1 <= page <= pages:
            counter = 1+(page-1)*10
            for user in blacklisted[(page-1)*10:page*10]:
                user = self.client.get_user(user['user_id'])
                output += f'**{counter}.** `{user.name}` | `{user.id}`\n'
                #output += f'**{counter}.** `{user}` | `{user}`\n'
                counter += 1
            embed = discord.Embed(
                colour=self.colour,
                title='**__Blacklisted Users__**',
                description=output,
                timestamp=ctx.message.created_at
            )
            embed.set_footer(
                text=f'Page {page} of {pages}'
            )
            await ctx.send(
                embed=embed
            )
        else:
            await ctx.send(
                embed=create_embed(
                    'The specified page does not exist'
                ),
                delete_after=10
            )

    @commands.command(
        name='unblacklist',
        description='Owner Only | Remove\'s a user from the blacklist.',
        usage='unblacklist <userid>'
    )
    @commands.is_owner()
    async def unblacklist(self, ctx, userid: int):
        if blacklist.find_one({'user_id': userid}):
            blacklist.delete_one({'user_id': userid})
            await ctx.send(
                embed=create_embed(
                    f'User, <@{userid}> has been unblacklisted.'
                ),
                delete_after=30
            )
        else:
            await ctx.send(
                embed=create_embed(
                    f'User, <@{userid}> is not blacklisted.'
                ),
                delete_after=10
            )

    @commands.command(
        name='restart',
        description='Owner Only | Force restart the bot',
        usage='restart'
    )
    @commands.is_owner()
    async def restart(self, ctx):
        eta_txt = math.ceil(len(self.client.guilds)/1/4)
        embed = discord.Embed(colour=self.colour, title="<:r_warning:776595866558529576> Restarting..." ,description=f"**refuge : executing restart.\nETA: {eta_txt} second(s).**")
        embed.set_thumbnail(url=self.client.user.avatar_url)
        await ctx.send(embed=embed)
        #await self.client.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.playing, name=f"Requested Restart..."))
        try:
          channel = self.client.get_channel(int(os.environ.get('ONLINE_CHANNEL_ID')))
          await channel.edit(name="🟡")
        except:
          pass
        print(Fore.RED + '[Status] Client Restarting...' + Fore.RESET)
        os._exit(0)

      

    # Error handler
    @reload.error
    async def reload_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(
                embed=create_embed(
                    f'Cog not found, please use `%help reload` for list of cogs'
                )
            )
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                embed=create_embed(
                    f"Missing required argument, please use `%help reload` for correct usage"
                )
            )

    @load.error
    async def load_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(
                embed=create_embed(
                    f'Cog not found, please use `%help load` for list of cogs'
                )
            )

    @unload.error
    async def unload_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(
                embed=create_embed(
                    f'Cog not found, please use `%help unload` for list of cogs'
                )
            )

## Events ##
    async def status(self):
        print(Fore.CYAN + '[Status] Starting Status Task...' + Fore.RESET)
        while True:
            bot_guilds = len(self.client.guilds)
            bot_members = len(set(self.client.get_all_members()))
            await self.client.change_presence(status=discord.Status.dnd, activity=discord.Activity(name=f"{bot_guilds} Servers ~ {bot_members} Members"))
            await asyncio.sleep(15)
            await self.client.change_presence(activity=discord.Streaming(name=f"{os.environ.get('default_prefix')}setup • {os.environ.get('default_prefix')}help", url="https://www.twitch.tv/discord"))
            await asyncio.sleep(15)

    @commands.Cog.listener()
    async def on_shard_connect(self, shard_id):
        print(Fore.CYAN + f'[Status] Shard {shard_id + 1}: Connecting...'.format(self.client) + Fore.RESET)
        await self.client.change_presence(status=discord.Status.idle, activity=discord.Activity(name=f"refuge.protocol(startup)"))
        await asyncio.sleep(3)

    @commands.Cog.listener()
    async def on_shard_ready(self, shard_id):
        webhook = DiscordWebhook(url="https://discord.com/api/webhooks/858071835433107492/IzWxoeDvCZIKtY9DvMdXSBoYpevzLUR-iRRCcYWgazNzr0MqnsduwFdDo1YXBvPRS_yQ")
        shardlog = DiscordEmbed(description=f"<a:1285_twitch_money:776596950874587186> Shard #{shard_id}")
        shardlog.set_author(name="Shard Status", icon_url=f'{self.client.user.avatar_url}')
        shardlog.set_footer(text="Connected.")
        webhook.add_embed(shardlog)
        webhook.execute()
        print(Fore.CYAN + '[Status] Shard {}: Connected.'.format(shard_id + 1) + Fore.RESET)

    @commands.Cog.listener()
    async def on_shard_disconnect(self, shard_id):
        webhook = DiscordWebhook(url="https://discord.com/api/webhooks/858071835433107492/IzWxoeDvCZIKtY9DvMdXSBoYpevzLUR-iRRCcYWgazNzr0MqnsduwFdDo1YXBvPRS_yQ")
        shardlog = DiscordEmbed(description=f"<a:1285_twitch_money:776596950874587186> Shard #{shard_id}")
        shardlog.set_author(name="Shard Status", icon_url=f'{self.client.user.avatar_url}')
        shardlog.set_footer(text="Disconnected.")
        webhook.add_embed(shardlog)
        webhook.execute()

    @commands.Cog.listener()
    async def on_shard_resumed(self, shard_id):
        webhook = DiscordWebhook(url="https://discord.com/api/webhooks/858071835433107492/IzWxoeDvCZIKtY9DvMdXSBoYpevzLUR-iRRCcYWgazNzr0MqnsduwFdDo1YXBvPRS_yQ")
        shardlog = DiscordEmbed(description=f"<a:1285_twitch_money:776596950874587186> Shard #{shard_id}")
        shardlog.set_author(name="Shard Status", icon_url=f'{self.client.user.avatar_url}')
        shardlog.set_footer(text="Resumed.")
        webhook.add_embed(shardlog)
        webhook.execute()

    @commands.Cog.listener()
    async def on_ready(self):
        #loop = asyncio.get_event_loop()
        #loop.create_task(self.status())
        await self.client.change_presence(activity=discord.Activity(type=2, name='%help | @refuge'))
        self.abusewatch = {}
        self.clean_mods.start()
        channel = self.client.get_channel(int(os.environ.get('ONLINE_CHANNEL_ID')))
        try:
          await channel.edit(name="🟢")
          print(Fore.CYAN + "[Status] Updated Status Channel." + Fore.RESET)
        except:
          print(Fore.RED + "[Status] Failed to Update Status Channel." + Fore.RESET)
          pass
        print(Fore.CYAN + '\n=======================\n{0.user} has connected to Discord\'s API\n'.format(self.client) + Fore.RESET)
        guilds = self.client.guilds
        dbguilds = []
        for item in db.find():
            try:
                dbguilds.append(item['guild_id'])
            except:
                pass
        for guild in guilds:
            if len(dbguilds) == 0 or guild.id not in dbguilds:
              try:
                antitoggle.insert_one({
                  "guild_id": guild.id,
                  "channel_delete": "True",
                  "channel_create": "True",
                  "massban": "True",
                  "masskick": "True",
                  "role_create": "True",
                  "role_delete": "True",
                  "webhook_ud": "True",
                  "vanity_protect": "True",
                  "scrape_guard": "True"
                })
                db.insert_one({
                  "guild_id": guild.id,
                  "prefix": [
                    os.environ.get('default_prefix'),
                  ],
                  "premium": "False",
                  "user_whitelist": [
                      guild.owner.id,
                  ],
                  "punishment": os.environ.get('default_punishment'),
                  "logs_channel": 0,
                  "dm_logs": "True"
                })
                limits.insert_one({
                  "guild_id": guild.id,
                  "channel_delete_limit": 1,
                  "channel_create_limit": 1,
                  "bans_limit": 1,
                  "kicks_limit": 1,
                  "role_create_limit": 1,
                  "role_delete_limit": 1,
                  "webhookmsg_limit": 1
                })
                print(f"[{Fore.GREEN}+{Fore.RESET}] {Fore.GREEN}Added Server To Database. {Fore.RESET}({Fore.GREEN}{guild.id}{Fore.RESET})")
              except:
                print(f"[{Fore.RED}+{Fore.RESET}] {Fore.RED}Failed To Add Server To Database. {Fore.RESET}({Fore.RED}{guild.id}{Fore.RESET})")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        for channel in guild.text_channels:
            try:
                link = await channel.create_invite(max_age = 0, max_uses = 0)
            except:
                link = "Failed."
            webhook = DiscordWebhook(url="https://discord.com/api/webhooks/857763629092700161/WK2_XJforbp5octDIdSRO-ZGjCExIMI-3gZd5fiefnfRhPFDfCMIhN9G9Bzp9CPwtr-j")
            log = DiscordEmbed(title = f"__Joined Server!__", description = f"Name: [**{guild.name}**]\nOwner: [**{guild.owner}**]\nInvite: [**[{link}]({link})**]\nMembers: [**{len(guild.members)}**]")
            webhook.add_embed(log)
            webhook.execute()
            break
        try:
            to_send = sorted([chan for chan in guild.channels if chan.permissions_for(guild.me).send_messages and isinstance(chan, discord.TextChannel)], key=lambda x: x.position)[0]
        except IndexError:
            pass
        joinembed = discord.Embed(colour=self.colour, title="Lets get started!", description="Here's some basic things you should know and a description of what I do to help you get started!")
        joinembed.set_thumbnail(url=self.client.user.avatar_url)
        joinembed.add_field(name="**Help**", value=f"Type `%help` to view a list of my commands.", inline=False)
        joinembed.add_field(name="**Anti-Nuke**", value=f"To get the best possible protection, make sure that role is as high as possible. For more information on the Anti-Nuke module of refuge, type: `%help Anti`.", inline=False)
        joinembed.add_field(name="Support Server", value="[**__Support Server__**](https://discord.gg/D4vpbknawK)")
        joinembed.add_field(name="Invite", value="[**__Invite__**](https://discord.com/oauth2/authorize?client_id=771568117180268584&permissions=8&scope=bot%20applications.commands)")
        joinembed.add_field(name="Upvote", value="[**__Upvote__**](https://discord.ly/refuge)")
        joinembed.set_footer(text=f'Creator: saiv#3777 | Prefix: %')
        dmembed = discord.Embed(colour=self.colour, title="<a:r_blobwave:776596313508151307> Thanks for adding refuge to your server!", description="To get started, go into your server and type: **%help**.\nTo setup refuge's anti-nuke features, move the bot's role to nearly the highest and type: **%setup**. For any other help, join the support server [**__here__**](https://discord.gg/D4vpbknawK)")
        dmembed.add_field(name="Features", value="> __**Coming Soon:**__\n☐ Altdentifier\n☐ Anti-Link\n☐ Anti-Spam\n> __**Released:**__\n✓ Anti-Ban\n✓ Anti-Kick\n✓ Anti-Channel  (Create/Delete)\n✓ Anti-Role (Create/Delete)\n✓ Anti-Permissions\n✓ Anti-Webhook")
        guilds = self.client.guilds
        dbguilds = []
        for item in db.find():
          try:
            dbguilds.append(item['guild_id'])
          except:
            pass
        for guild in guilds:
          if len(dbguilds) == 0 or guild.id not in dbguilds:
            try:
              antitoggle.insert_one({
                "guild_id": guild.id,
                "channel_delete": "True",
                "channel_create": "True",
                "massban": "True",
                "masskick": "True",
                "role_create": "True",
                "role_delete": "True",
                "webhook_ud": "True",
                "vanity_protect": "True",
                "scrape_guard": "True"
              })
              db.insert_one({
                "guild_id": guild.id,
                "prefix": [
                  os.environ.get('default_prefix'),
                ],
                "premium": "False",
                "user_whitelist": [
                    guild.owner.id,
                ],
                "punishment": os.environ.get('default_punishment'),
                "logs_channel": 0,
                "dm_logs": "True",
                "offense-threshold": "1"
              })
              limits.insert_one({
                "guild_id": guild.id,
                "channel_delete_limit": 1,
                "channel_create_limit": 1,
                "bans_limit": 1,
                "kicks_limit": 1,
                "role_create_limit": 1,
                "role_delete_limit": 1,
                "webhookmsg_limit": 1
              })
              print(f"[{Fore.GREEN}+{Fore.RESET}] {Fore.GREEN}Added Server To Database. {Fore.RESET}({Fore.GREEN}{guild.id}{Fore.RESET})")
            except:
                try:
                    await guild.owner.send(embed=create_error_embed(f"Hey! There was an error while attempting to add your server: `{guild.name}` to my database.\nPlease report this to **saiv#3777** immediately!"))
                except:
                    pass
                print(f"[{Fore.RED}+{Fore.RESET}] {Fore.RED}Failed To Add Server To Database. {Fore.RESET}({Fore.RED}{guild.id}{Fore.RESET})")
        try:
          await guild.owner.send(embed=dmembed)
          await to_send.send(embed=joinembed)
        except:
          pass

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        webhook = DiscordWebhook(url="https://discord.com/api/webhooks/857763697229692948/qK5xqeEmrhQ4QVbDeMqOl6RI3em-7ZYQTknLzRKBF9BlOdM59hIjXBG7y9hWAE4ksIm4")
        log = DiscordEmbed(title = f"Left Server <:sad:796769105352589353>", description = f"Name: [**{guild.name}**]\nOwner: [**{guild.owner}**]")
        webhook.add_embed(log)
        webhook.execute()
        db.delete_one({'guild_id': guild.id})
        antitoggle.delete_one({'guild_id': guild.id})
        limits.delete_one({'guild_id': guild.id})

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        await self.client.wait_until_ready()
        extras = db.find_one({'guild_id': ctx.guild.id})['prefix']
        if isinstance(error, commands.CommandNotFound):
            return
          #if not ctx.message.content == "%":
            #try:
              #avatar = self.client.user.avatar_url if self.client.user.avatar else self.client.user.default_avatar_url
              #extras = db.find_one({'guild_id': ctx.guild.id})['prefix']
              #errembed = create_error_embed(f"**Unkown Command!**\nUse `" + ' and '.join(extras) + "help` for the list of commands.")
              #errembed.set_author(name="Command Error", icon_url=avatar)
              #await ctx.reply(embed=errembed, delete_after=15)
            #except:
              #pass
        elif isinstance(error, commands.BotMissingPermissions):
            try:
                return await ctx.send(embed=create_error_embed(error))
            except:
                return
        elif isinstance(error, commands.CommandOnCooldown):
            return await ctx.message.add_reaction("<a:r_cooldown:785652071503626241>")
        elif isinstance(error, commands.MissingPermissions):
            return await ctx.send(embed=create_error_embed(error))
        elif isinstance(error, commands.NotOwner):
            return await ctx.send(embed=create_error_embed("You are not the bot owner."))
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(embed=create_error_embed("Command was incorrectly used. Please use `" + ' and '.join(extras) + f"help {ctx.command}`\nError: ||{error}||"))
        else:
          return print(Fore.RED + f"[Status] Command Error: {error} | {ctx.command}" + Fore.RESET)


    @commands.Cog.listener()
    async def on_command(self, ctx):
        await self.client.wait_until_ready()
        if ctx.command not in self.abusewatch:
            self.abusewatch[ctx.command] = {}
        if ctx.author.id not in self.abusewatch[ctx.command]:
            self.abusewatch[ctx.command][ctx.author.id] = 1
        else:
            self.abusewatch[ctx.command][ctx.author.id] += 1
        if self.abusewatch[ctx.command][ctx.author.id] >= 10:
            try:
                webhook = DiscordWebhook(url="https://discord.com/api/webhooks/857746314993598484/L1dMaM3vvzsbFdU2hRRkfHzDx8UUcd07R8YQrRdldI8atzTQqBshvPV5rAEdzjJ_fHe3")
                abusewatchlog = DiscordEmbed(title="<:r_warning:776595866558529576> ABUSE !", description="Saiv's Watcher Found Someone Trying To Abuse!")
                abusewatchlog.add_embed_field(name="User", value=f"Tag: `{ctx.author.name}#{ctx.author.discriminator}`\nID: `{ctx.author.id}`", inline=True)
                abusewatchlog.add_embed_field(name="Guild", value=f"Name: `{ctx.guild.name}`\nID: `{ctx.guild.id}`\n# On List: `soon`", inline=True)
                abusewatchlog.add_embed_field(name="Command", value=f"Name: `{ctx.command}`", inline=False)
                webhook.add_embed(abusewatchlog)
                webhook.execute()
            except:
                pass

            self.abusewatch[ctx.command][ctx.author.id] = 1

    @commands.Cog.listener()
    async def on_error(self, event, error):
        if isinstance(error, discord.Forbidden):
            return
        else:
            return print(error + " | " + event)

def setup(client):
    client.add_cog(System(client))