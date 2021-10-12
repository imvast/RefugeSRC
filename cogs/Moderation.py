# Imports
import discord, os, pymongo, random
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


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.db = db
        self.colour = discord.Colour.random()
        print(f"{C.CYAN}[Status] Cog Loaded: Moderation" + C.RESET)


    @commands.command(
        name="addrole", 
        description="Gives the mentioned user a role.", 
        usage="addrole <user> <role>",
        aliases=["giverole"]
    )
    @commands.cooldown(1, 5, commands.BucketType.channel)
    @blacklist_check()
    @commands.has_guild_permissions(manage_roles=True)
    async def addrole(self, ctx, member: discord.Member, role: discord.Role):
      if member.top_role >= ctx.author.top_role:
        return await ctx.send(embed=create_error_embed("The provided user has roles that are above or have the same role as you."))
      await member.add_roles(role)
      await ctx.send(embed=create_embed(f"{role.mention} has been given to, {member.mention}"))

    @commands.command(
        name="removerole", 
        description="Removes a role from the mentioned user.", 
        usage="removerole <user> <role>",
        aliases=["remrole"]
    )
    @commands.cooldown(1, 5, commands.BucketType.channel)
    @blacklist_check()
    @commands.has_guild_permissions(manage_roles=True)
    async def removerole(self, ctx, member: discord.Member, role: discord.Role):
      if member.top_role >= ctx.author.top_role:
        return await ctx.send(embed=create_error_embed("The provided user has roles that are above or have the same role as you."))
      await member.remove_roles(role)
      await ctx.send(embed=create_embed(f"{role.mention} has been removed from, {member.mention}"))


    @commands.command(
        name='kick',
        description='Kick someone from the server',
        usage="kick <user>"
    )
    @blacklist_check()
    @commands.has_guild_permissions(kick_members=True)
    @commands.cooldown(2, 5, commands.BucketType.channel)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await ctx.message.delete()
        guild = ctx.guild
        if ctx.author == member:
            await ctx.send(
                embed=create_error_embed('Do you really want to kick yourself?'), delete_after=20)
        elif ctx.author.top_role <= member.top_role:
            await ctx.send(embed=create_error_embed(f"**You can't kick a member above you.**"))
        elif ctx.guild.owner == member:
            await ctx.send(
                embed=create_error_embed('You cannot kick the server owner'), delete_after=20)
        else:
            if reason == None:
                try:
                    try:
                    #    await member.send(embed=create_embed(f"**You have been kicked from {guild.name}**"))
                        await member.kick(reason=f"Responsible: {ctx.author}")
                        kickembed = discord.Embed(description=f'**{member} has been kicked.**', colour=self.colour)
                        kickembed.set_footer(text=f"Responsible: {ctx.author}")
                        await ctx.send(embed=kickembed)
                    except:
                        await member.kick(reason=f"Responsible: {ctx.author}")
                        kick2embed = discord.Embed(description=f'**{member} has been kicked.**', colour=self.colour)
                        kick2embed.set_footer(text=f"Responsible: {ctx.author}")
                        await ctx.send(embed=kick2embed)
                except Exception as e:
                    await ctx.send(embed=create_error_embed(f"**Failed to kick, {member}**\n||{e}||"))
            else:
                try:
                #    await member.send(embed=create_embed(f"**You have been kicked from {guild.name} for *{reason}***"))
                    await member.kick(reason=reason)
                    kick3embed = discord.Embed(description=f'**{member} was kicked.**\nReason: `{reason}`', colour=self.colour)
                    kick3embed.set_footer(text=f"Responsible: {ctx.author}")
                    await ctx.send(embed=kick3embed)
                except Exception as e:
                    await ctx.send(embed=create_error_embed(f"**Failed to kick, {member}**\n||{e}||"))

    @commands.command(
        name='ban',
        description='Bans mentioned user.',
        usage="ban <user> [reason]",
        inline=True
    )
    @blacklist_check()
    @commands.has_guild_permissions(ban_members=True)
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
            await ctx.message.delete()
            guild = ctx.guild
            if ctx.author == member:
                await ctx.send(embed=create_error_embed(f'{ctx.author.mention}, Do you really want me to ban you?'), delete_after=20)
            elif ctx.author.top_role <= member.top_role:
                await ctx.send(embed=create_error_embed(f"**You can't ban a member above you.**"))
            elif ctx.guild.owner == member:
                await ctx.send(
                    embed=create_error_embed(':joy: Server owners can\'t be banned!!'), delete_after=20) # set :joy: to anim emoji
            else:
                if reason == None:
                    try:
                        try:
                        #   await member.send(embed=create_embed(f"**You have been banned from, {guild.name}**"))
                           await member.ban(reason=f"Responsible: {ctx.author}")
                           banembed = discord.Embed(description=f'**{member} has been banned.**', colour=self.colour)
                           banembed.set_footer(text=f"Responsible: {ctx.author}")
                           await ctx.send(embed=banembed)
                        except:
                           await member.ban(reason=f"Responsible: {ctx.author}")
                           ban2embed = discord.Embed(description=f'**{member} has been banned.**', colour=self.colour)
                           ban2embed.set_footer(text=f"Responsible: {ctx.author}")
                           await ctx.send(embed=ban2embed)
                    except Exception as e:
                        await ctx.send(embed=create_error_embed(f"**Failed to ban, {member}**\n||{e}||"))
                else:
                    try:
                        try:
                        #    await member.send(embed=create_embed(f"**You have been banned from {guild.name} for *{reason}***"))
                            await member.ban(reason=reason)
                            ban3embed = discord.Embed(description=f'**{member} has been banned.**\nReason: `{reason}`', colour=self.colour)
                            ban3embed.set_footer(text=f"Responsible: {ctx.author}")
                            await ctx.send(embed=ban3embed)
                        except:
                            await member.ban(reason=reason)
                            ban4embed = discord.Embed(description=f'**{member} has been banned.**\nReason: `{reason}`', colour=self.colour)
                            ban4embed.set_footer(text=f"Responsible: {ctx.author}")
                            await ctx.send(embed=ban4embed)
                    except Exception as e:
                        await ctx.send(embed=create_error_embed(f"**Failed to ban, {member}**\n||{e}||"))

    @commands.command(
        name="idban",
        description="Bans a user thats not in the server.",
        usage="idban <userid> [reason]",
        inline=True
    )
    @blacklist_check()
    @commands.cooldown(1, 5, commands.BucketType.channel)
    @commands.has_permissions(ban_members=True)
    async def idban(self, ctx, userid, *, reason=None):
            await ctx.message.delete()
            try:
                userid = int(userid)
            except:
                await ctx.send(embed=create_embed('Invalid ID'))
        
            try:
                await ctx.guild.ban(discord.Object(userid), reason=reason)
                idbanembed = discord.Embed(description=f'**{userid} has been banned.**\nReason: `{reason}`', colour=self.colour)
                idbanembed.set_footer(text=f"Responsible: {ctx.author}")
                await ctx.send(embed=idbanembed)
            except Exception as e:
                await ctx.send(embed=create_error_embed(f"**Failed to idban, {userid}**\n||{e}||"))

    @commands.command(
        name='unban',
        description='Unbans the specified user.',
        usage="unban <user>",
        inline=True
    )
    @blacklist_check()
    @commands.has_permissions(ban_members=True)
    @commands.cooldown(1, 3, commands.BucketType.channel)
    async def unban(self, ctx, userid):
            await ctx.message.delete()
            if ctx.author == userid:
                await ctx.send(embed=create_error_embed(f"You aren't banned."), delete_after=10)
            else: 
                try:
                   user = discord.Object(id=userid)
                   await ctx.guild.unban(user, reason=f"Responsible: {ctx.author}")
                   unbanembed = discord.Embed(description=f'**{userid} has been unbanned.**', colour=self.colour)
                   unbanembed.set_footer(text=f"Responsible: {ctx.author}")
                   await ctx.send(embed=unbanembed)
                except Exception as e:
                   await ctx.send(embed=create_error_embed(f"**Failed to unban, {userid}**\n||{e}||"))


    @commands.command(
        name="mute",
        description="Mutes the mentioned user.",
        usage="mute <user> [reason]"
    )
    @blacklist_check()
    @commands.has_permissions(manage_roles=True)
    @commands.cooldown(2, 5, commands.BucketType.channel)
    async def mute(self, ctx, member: discord.Member, *, reason: str = None):
            await ctx.message.delete()
            guild = ctx.guild
            muted_role = next((g for g in ctx.guild.roles if g.name.lower() == "muted"), None)
            if member.top_role >= ctx.author.top_role:
              await ctx.send(embed=create_error_embed("Bro? That's not how this works, lol. (they are above/have the same role as you)"))
              return
            if not muted_role:
              try:
                try:
                  await guild.create_role(name="Muted")
                  #await member.send(embed=create_embed(f"**You have been muted in {guild.name}**\nReason: `{reason}`"))
                  await member.add_role(muted_role, reason=f"Responsible: {ctx.author}")
                  muteembed = discord.Embed(description=f'**{member} has been muted.**\nReason: `{reason}`', colour=discord.Colour.from_rgb(136,3,252))
                  muteembed.set_footer(text=f"Responsible: {ctx.author}")
                  await ctx.send(embed=muteembed)
                except:
                  await guild.create_role(name="Muted")
                  await member.add_role(muted_role, reason=f"Responsible: {ctx.author}")
                  mute2embed = discord.Embed(description=f'**{member} has been muted.**\nReason: `{reason}`', colour=discord.Colour.from_rgb(136,3,252))
                  mute2embed.set_footer(text=f"Responsible: {ctx.author}")
                  await ctx.send(embed=mute2embed)
              except Exception as e:
                await ctx.send(embed=create_error_embed(f"**Failed to mute, {member}**\n||{e}||"))
            else:
                try:
                    try:
                        #await member.send(embed=create_embed(f"**You have been muted in {guild.name}**\nReason: `{reason}`"))
                        await member.add_role(muted_role, reason=f"Responsible: {ctx.author}")
                        muteembed = discord.Embed(description=f'**{member} has been muted.**\nReason: `{reason}`', colour=self.colour)
                        muteembed.set_footer(text=f"Responsible: {ctx.author}")
                        await ctx.send(embed=muteembed)
                    except:
                        await member.add_role(muted_role, reason=f"Responsible: {ctx.author}")
                        mute2embed = discord.Embed(description=f'**{member} has been muted.**\nReason: `{reason}`', colour=self.colour)
                        mute2embed.set_footer(text=f"Responsible: {ctx.author}")
                        await ctx.send(embed=mute2embed)
                except Exception as e:
                    await ctx.send(embed=create_error_embed(f"**Failed to mute, {member}**\n||{e}||"))
              
    @commands.command(
        name="unmute",
        description="Unmutes the mentioned user.",
        usage="unmute <user> [reason]"
    )
    @blacklist_check()
    @commands.has_permissions(manage_roles=True)
    @commands.cooldown(1, 3, commands.BucketType.channel)
    async def unmute(self, ctx, member: discord.Member, *, reason: str = None):
            await ctx.message.delete()
            guild = ctx.guild
            muted_role = next((g for g in ctx.guild.roles if g.name.lower() == "muted"), None)
            if member.top_role >= ctx.author.top_role:
              await ctx.send(embed=create_error_embed("Bro? That's not how this works, lol. (they are above/have the same role as you)"))
              return
            if not muted_role:
                return await ctx.send(embed=create_error_embed(f"**{member} is not muted.**"))
            else:
                try:
                    try:
                        await member.send(embed=create_embed(f"**You are no longer muted in, {guild.name}**"))
                        await member.remove_roles(muted_role)
                        unmuteembed = discord.Embed(description=f'**{member.mention} has been unmuted.**\nReason: `{reason}`', colour=self.colour)
                        unmuteembed.set_footer(text=f"Responsible: {ctx.author}")
                        await ctx.send(embed=unmuteembed)
                    except:
                        await member.remove_roles(muted_role)
                        unmute2embed = discord.Embed(description=f'**{member.mention} has been unmuted.**\nReason: `{reason}`', colour=self.colour)
                        unmute2embed.set_footer(text=f"Responsible: {ctx.author}")
                        await ctx.send(embed=unmute2embed)
                except Exception as e:
                    await ctx.send(embed=create_error_embed(f"**Failed to unmute, {member}**\n||{e}||"))
                    
    @commands.command(
        name='purge',
        description='Mass delete messages (default = 15)',
        aliases=['clear'],
        usage="purge <amount>"
    )
    @blacklist_check()
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def purge(self, ctx, amount=15):
        await ctx.reply(embed=create_embed("Purging **{}** Messages...".format(amount)))
        await ctx.channel.purge(limit=amount+2)
        await ctx.send(embed=create_embed("<:r_check:780938741640200239> Successfully Purged **{}** Messages!".format(amount)), delete_after=5)

    @commands.command(
        name='nuke',
        description='Remakes current channel.',
        aliases=['nukechannel'],
        usage="nuke"
    )
    @blacklist_check()
    @commands.cooldown(1, 30, commands.BucketType.guild)
    @commands.has_permissions(manage_channels=True)
    async def nuke(self, ctx, arg=None):
            extras = db.find_one({'guild_id': ctx.guild.id})['prefix']
            await ctx.message.delete()
            if arg != None:
                await ctx.send(
                    embed=create_error_embed('Invalid command usage, please use `' + ' and '.join(extras) + 'help nuke` for info about the command.'), delete_after=10)
            else:
                counter = 0
                await ctx.send(embed=create_embed(f"Nuking Channel {ctx.channel.name}..."))
                channel_info = [ctx.channel.category,
                ctx.channel.position]
                channel_id = ctx.channel.id
                await ctx.channel.clone()
                await ctx.channel.delete()
                new_channel = channel_info[0].text_channels[-1]
                await new_channel.edit(position=channel_info[1])
                embed = discord.Embed(colour=self.colour, timestamp=ctx.message.created_at)
                embed.set_author(name=f"Channel Nuked.", icon_url=ctx.author.avatar_url)
                embed.set_footer(text=f"{ctx.author}")
                embed.set_image(url="https://cdn.discordapp.com/attachments/769749773401849896/776951922295963648/giphy-downsized-large.gif")
                await new_channel.send(embed=embed)

    @commands.command(
        name="lock",
        description="Locks down a channel.",
        usage="lock `#<channel>` [reason]",
    )
    @blacklist_check()
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def lock(self, ctx, channel:discord.TextChannel = None, *, reason=None):
            await ctx.message.delete()
            if channel is None: channel = ctx.channel
            try:
                await channel.set_permissions(ctx.guild.default_role, overwrite=discord.PermissionOverwrite(send_messages = False), reason=reason)
                await ctx.send(embed=create_embed(f"**#{channel}** has been locked.\nReason: `{reason}`"))
            except:
                await ctx.send(embed=create_error_embed(f"**Failed to lockdown, {channel}**"))
            else:
                pass

    @commands.command(
        name="unlock",
        description="Unlocks a channel.",
        usage="unlock `#<channel>`",
    )
    @blacklist_check()
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def unlock(self, ctx, channel:discord.TextChannel = None, *, reason=None):
            await ctx.message.delete()
            if channel is None: channel = ctx.channel
            try:
                await channel.set_permissions(ctx.guild.default_role, overwrite=discord.PermissionOverwrite(send_messages = True), reason=reason)
                await ctx.send(embed=create_embed(f"**#{channel}** has been unlocked.\nReason: `{reason}`"))
            except:
                await ctx.send(embed=create_error_embed(f"**Failed to unlock, {channel}**"))
            else:
                pass

    @commands.command(
        name="lockall",
        description="Locks down the server.",
        usage="lockall"
    )
    @blacklist_check()
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def lockall(self, ctx, server:discord.Guild = None, *, reason=None):
            await ctx.message.delete()
            if server is None: server = ctx.guild
            try:
                for channel in server.channels:
                    await channel.set_permissions(ctx.guild.default_role, overwrite=discord.PermissionOverwrite(send_messages = False), reason=reason)
                await ctx.send(embed=create_embed(f"**{server}** has been locked.\nReason: `{reason}`"))
            except:
                await ctx.send(embed=create_error_embed(f"**Failed to lockdown, {server}.**"))
            else:
                pass

    @commands.command(
        name="unlockall",
        description="Unlocks the server. | Warning: this unlocks every channel for the @everyone role.",
        usage="unlockall"
    )
    @blacklist_check()
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def unlockall(self, ctx, server:discord.Guild = None, *, reason=None):
            await ctx.message.delete()
            if server is None: server = ctx.guild
            try:
                for channel in server.channels:
                    await channel.set_permissions(ctx.guild.default_role, overwrite=discord.PermissionOverwrite(send_messages = True), reason=reason)
                await ctx.send(embed=create_embed(f"**{server}** has been unlocked.\nReason: `{reason}`"))  
            except:
                await ctx.send(embed=create_error_embed(f"**Failed to unlock, {server}**"))
            else:
                pass

# error handlers

    @unmute.error
    async def unmute_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(embed=create_error_embed('Please Specify a Member.'))
    
    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(embed=create_error_embed('Please Specify a Member.'))
            
    @nuke.error
    async def nuke_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(
                embed=create_error_embed(
                    f'You can only complete one  **1** nuke every **30 seconds**\nTime until next available channel nuke: {int(error.retry_after)}s'
                )
            )
  
    @idban.error
    async def idban_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(embed=create_error_embed('Please Specify a Member ID.'))
                                              
    
    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(embed=create_error_embed('Please Specify a Member.'))

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(embed=create_error_embed('Please Specify a Member.'))
  

    @unban.error
    async def unban_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(embed=create_error_embed('Please Specify a Member.'))

# Add cog
def setup(client):
    client.add_cog(Moderation(client))