import discord, pymongo, os, asyncio, random
from colorama import Fore as C
from discord.ext import commands
from discord.errors import Forbidden
from discord_components import *
from settings import *

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


async def send_embed(self, ctx, embed, components=None):
    try:
        if components==None:
            await ctx.reply(embed=embed)
        else:
            self.m = await ctx.reply(embed=embed, components=components)
    except Forbidden:
        try:
            await ctx.reply("Hey! It seems that I am unable to send embedded messages. Please check my permissions and try again.")
        except Forbidden:
            return


class Help(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.colour = 0x36373f
        print(f"{C.CYAN}[Status] Cog Loaded: Help" + C.RESET)

    @commands.command(description="shows categories", usage="help [command/category]")
    # @commands.client_has_permissions(add_reactions=True, embed_links=True)
    @commands.cooldown(1, 3, commands.BucketType.channel)
    @blacklist_check()
    async def help(self, ctx, type=None):
        """
        help antinuke
        """
        extras = db.find_one({'guild_id': ctx.guild.id})['prefix']
        if type is None:
            helpem = discord.Embed(
                title=f"refuge help menu", 
                description=f"`<>` = Required | `[]` = Recommended\nFor more information do, `" + ' and '.join(extras) + "help <command/category>`", 
                colour=self.colour, 
                timestamp=ctx.message.created_at
            )
            helpem.add_field(name="<:r_dshield:862408032108544019> Anti-Nuke", value="Anti-Nuke commands such as: `setup`.", inline=False)
            helpem.add_field(name="<:r_moderator:865008551969816586> Moderation", value="Advanced moderation commands to help moderators.", inline=False)
            helpem.add_field(name="<:r_infostill:782391173666045992> Information", value="Extra information such as: `botinfo` and `serverinfo`.", inline=False)
            helpem.set_footer(text=f"Warning: Some commands may not provide usage. (WIP)\nPrefix: " + ' and '.join(extras))
            await send_embed(self, ctx, helpem,
                components=[[
                    Button(style=ButtonStyle.grey, custom_id="antinuke", emoji=self.client.get_emoji(862408032108544019)),
                    Button(style=ButtonStyle.grey, custom_id="mod", emoji=self.client.get_emoji(865008551969816586)),
                    Button(style=ButtonStyle.grey, custom_id="information", emoji=self.client.get_emoji(782391173666045992)),
                ]],
            )
            active=True
            def check(res):
                return ctx.author == res.user and res.channel == ctx.channel

            while active == True:
              try:
                res = await self.client.wait_for("button_click", check=check, timeout=30)
                if res.custom_id == "antinuke":
                    commands = self.client.get_cog("AntiCmds").get_commands()
                    embed = discord.Embed(
                        title=f"Help > Anti-Nuke",
                        description='',
                        color=self.colour
                    )
                    for command in commands:
                        embed.description += "`%s` ・ %s\n" % (command, command.description)
                    await res.respond(
                        type=7,
                        embed=embed,
                        components=[[
                            Button(style=ButtonStyle.grey, custom_id="antinuke", emoji=self.client.get_emoji(862408032108544019), disabled=True),
                            Button(style=ButtonStyle.grey, custom_id="mod", emoji=self.client.get_emoji(865008551969816586)),
                            Button(style=ButtonStyle.grey, custom_id="information", emoji=self.client.get_emoji(782391173666045992)),
                        ]],
                    )
                if res.custom_id == "information":
                    commands = self.client.get_cog("Information").get_commands()
                    embed = discord.Embed(
                        title=f"Help > Information",
                        description='',
                        color=self.colour
                    )
                    for command in commands:
                        embed.description += "`%s` ・ %s\n" % (command, command.description)
                    await res.respond(
                        type=7,
                        embed=embed,
                        components=[[
                            Button(style=ButtonStyle.grey, custom_id="antinuke", emoji=self.client.get_emoji(862408032108544019)),
                            Button(style=ButtonStyle.grey, custom_id="mod", emoji=self.client.get_emoji(865008551969816586)),
                            Button(style=ButtonStyle.grey, custom_id="information", emoji=self.client.get_emoji(782391173666045992), disabled=True),
                        ]],
                    )
                if res.custom_id == "mod":
                    commands = self.client.get_cog("Moderation").get_commands()
                    embed = discord.Embed(
                        title=f"Help > Moderation",
                        description='',
                        color=self.colour
                    )
                    for command in commands:
                        embed.description += "`%s` ・ %s\n" % (command, command.description)
                    await res.respond(
                        type=7,
                        embed=embed,
                        components=[[
                            Button(style=ButtonStyle.grey, custom_id="antinuke", emoji=self.client.get_emoji(862408032108544019)),
                            Button(style=ButtonStyle.grey, custom_id="mod", emoji=self.client.get_emoji(865008551969816586), disabled=True),
                            Button(style=ButtonStyle.grey, custom_id="information", emoji=self.client.get_emoji(782391173666045992)),
                        ]],
                    )
              except asyncio.TimeoutError:
                active=False
                await self.m.edit(
                    components=[[
                        Button(style=ButtonStyle.grey, custom_id="antinuke", emoji=self.client.get_emoji(862408032108544019), disabled=True),
                        Button(style=ButtonStyle.grey, custom_id="mod", emoji=self.client.get_emoji(865008551969816586), disabled=True),
                        Button(style=ButtonStyle.grey, custom_id="information", emoji=self.client.get_emoji(782391173666045992), disabled=True),
                    ]],
                )
        cog = self.client.get_cog(type)
        if type is None:
            pass
        if type.lower() == "system":
            return await ctx.send(embed=create_error_embed("**Invalid Usage > Unknown Command**"))
        elif type.lower() in ("anti-nuke", "antinuke", "anti"):
            cog = self.client.get_cog("AntiCmds")
            type = "Anti-Nuke"
        elif type.lower() in ("mod", "moderation"):
            cog = self.client.get_cog("Moderation")
            type = "Moderation"
        if cog is None:
            command = self.client.get_command(type)
            if command is None:
                return await ctx.send(embed=create_error_embed("**Invalid Usage > Unknown Command**"))
            embed = discord.Embed(title=f"Help > {command}", colour=self.colour)
            if command.description == None or command.description == '':
                embed.add_field(name="Description", value="・ None", inline=False)
            else:
                embed.add_field(name="Description", value=f"・ `{command.description}`", inline=False)
            if command.usage == None:
                embed.add_field(name="Usage", value="・ None", inline=False)
            else:
                embed.add_field(name="Usage", value="・ `" + ' and '.join(extras) + f"{command.usage}`", inline=False)
            cmdaliases = ""
            if not command.aliases:
                cmdaliases="・ None"
            else:
                for alias in command.aliases:
                    cmdaliases += f"・ `{alias}`\n"
            embed.add_field(name="Aliases", value=f"{cmdaliases}", inline=False)
            if command.help == None:
                embed.add_field(name="Example", value="・ None", inline=False)
            else:
                embed.add_field(name="Example", value="・ `" + ' and '.join(extras) + f"{command.help}`", inline=False)
            return await send_embed(self, ctx, embed)
        else:
            commands = cog.get_commands()
            embed = discord.Embed(
                title=f"Help > {type}",
                description='',
                color=self.colour
            )
            for command in commands:
                embed.description += "`%s` ・ %s\n" % (command, command.description)
            return await send_embed(self, ctx, embed)


    @commands.command(
        name='setprefix',
        description='Sets the custom prefix for the server',
        usage=f"setprefix <new prefix>"
    )
    @blacklist_check()
    @commands.has_guild_permissions(manage_guild=True)
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def setprefix(self, ctx, new_prefix: str):
        db.update_one({'guild_id': ctx.guild.id}, {'$set': {'prefix': new_prefix}})
        await ctx.send(
            embed=create_embed(
                f'・ Prefix changed to `{new_prefix}`'
            )
        )


def setup(client):
    client.add_cog(Help(client))