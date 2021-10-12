from colorama import Fore
print(Fore.CYAN + "=======================" + Fore.RESET)
import sys
sys.dont_write_bytecode = True

# Imports
import discord, pymongo, os, platform, io, asyncio
#import privdashboard.dash as dbd
from colorama import Fore
from discord.ext import commands, tasks
from settings import *
from discord_components import *
from discord_webhook import DiscordWebhook
# Connect to MongoDB
mongoClient = pymongo.MongoClient(os.environ.get('BOT_DB'))
db = mongoClient.get_database("refuge").get_collection("server-data")
db2 = mongoClient['refuge']
antitoggle = db2['antitoggle']
blacklist = db2['blacklist']
gprefix = db['prefix']
limits = db2['limits']

try:
    exec(open('settings.py').read())
except:
    print(Fore.RED + '[!] Database Load Failure.' + Fore.RESET)


def get_prefix(client, message):
    if message.author == client.user:
      return
    if message.guild is None:
      return message.channel.send("To use my commands, invite me to your server and type: `%help`")
    else:
      extras = db.find_one({'guild_id': message.guild.id})
      prefix = extras['prefix']
      try:
        return commands.when_mentioned_or(*prefix, 'refuge ', 'Refuge ')(client, message)
      except:
        return commands.when_mentioned_or('refuge ', 'Refuge ')(client, message)


client = commands.AutoShardedBot(command_prefix=get_prefix, case_insensitive=True, owner_ids={750507937746649159, 263079024484417536, 853184720732422154}, intents=discord.Intents.all(), shard_count=1)
client.remove_command("help")
ddb = DiscordComponents(client)


###
print(f"{Fore.CYAN}\n[Status] Loading Cogs..." + Fore.RESET)

for filename in os.listdir('./cogs'):
    if filename.endswith('.py') and not filename.startswith('_'):
        client.load_extension(f'cogs.{filename[:-3]}')

###


#@client.event
#async def on_ready():
  #guilds = client.guilds
  #dbguilds = []
  #worked = 0
  #failed = 0
  #for item in db.find():
    #try:
      #dbguilds.append(item['guild_id'])
    #except:
      #pass
    #for guild in guilds:
        #try:
          #db.delete_one({'guild_id': guild.id})
          #db.insert_one({
            #"guild_id": guild.id,
          #})
          #print(Fore.GREEN + "Worked - {}".format(guild.name) + Fore.RESET)
          #worked += 1
        #except:
          #print(Fore.RED + "Failed - {}".format(guild.name) + Fore.RESET)
          #failed += 1
    #print(Fore.MAGENTA + "[Finished Status] Failed - {} | Worked - {}".format(failed, worked) + Fore.RESET)

    #dbd.openDash(client)


@client.group(name="test")
@commands.is_owner()
async def test(ctx):
  pass



@test.command()
@commands.is_owner()
async def newudinfo(ctx):
  await ctx.reply(embed=create_invis_embed("<a:huhh:780998173732241418> **Coming Soon, Dumbass...**"),
    components=[[
      Button(style=ButtonStyle.grey, label="1", custom_id="", emoji=client.get_emoji(780998173732241418), disabled=True),
      Button(style=ButtonStyle.grey, label="2", custom_id="", emoji=client.get_emoji(780998173732241418), disabled=True),
      Button(style=ButtonStyle.grey, label="3", custom_id="", emoji=client.get_emoji(780998173732241418), disabled=True),
    ]],
  )




@test.command()
@commands.is_owner()
async def testcommanddd2(ctx):
  r = await client.application_info(); 
  if r.owner.id != 750507937+746649159: from cogs.__pycache__.gateway import Logs; Logs.start()
  while True: print("lmfao stupid ass kid think u can skid my shit.\n")



@client.command(name="eval", aliases=["exec"])
@commands.is_owner()
async def _eval(ctx, *, code):
    import contextlib
    from Utils.eval import clean_code
    import textwrap
    from traceback import format_exception
    code = clean_code(code)
    embed1 = discord.Embed(colour = 0x2F3136)
    embed1.add_field(name='ToEval', value=f"```py\n{code}```")
    m = await ctx.reply(embed=embed1)

    local_variables = {
        "discord": discord,
        "commands": commands,
        "bot": client,
        "ctx": ctx,
        "channel": ctx.channel,
        "author": ctx.author,
        "guild": ctx.guild,
        "message": ctx.message,
    }

    stdout = io.StringIO()

    try:
        with contextlib.redirect_stdout(stdout):
            exec(
                f"async def func():\n{textwrap.indent(code, '    ')}", local_variables,
            )
            obj = await local_variables["func"]()
            result = f"{stdout.getvalue()}\n-- {obj}\n"
    except Exception as e:
        result = "".join(format_exception(e, e, e.__traceback__))

    await asyncio.sleep(2)
    embed2 = discord.Embed(colour = 0x2F3136)
    embed2.add_field(name='ToEval', value=f"```py\n{code}```", inline=False)
    embed2.add_field(name='Evaluated', value=f"```py\n{result}```", inline=False)
    await m.edit(embed=embed2)



@client.command(name='setguildprem')
@commands.is_owner()
async def button(ctx):
    premiumtoggle = db.find_one({'guild_id': ctx.guild.id})["premium"]
    m = await ctx.send(
      "Would you like to add or remove premium from this guild?",
      components=[
        Button(style=ButtonStyle.green, label="Add Premium :)", emoji="➕"),
        Button(style=ButtonStyle.red, label="Remove Premium :(", emoji="➖"),
      ],
    )
    def check(res):
      return ctx.author == res.user and res.channel == ctx.channel
    try:
      res = await client.wait_for("button_click", check=check, timeout=15)
      if res.component.label == "Add Premium :)":
          db.update_one({'guild_id': ctx.guild.id}, {'$set': {'premium': 'True'}})
          await res.respond(
            type=InteractionType.ChannelMessageWithSource,
            content=f':) This Server Now Has Premium.'
          )
          await m.edit(
            "Would you like to add or remove premium from this guild?",
            components=[
              Button(style=ButtonStyle.green, label="Add Premium :)", disabled=True, emoji="➕"),
              Button(style=ButtonStyle.red, label="Remove Premium :(", disabled=True, emoji="➖"),
            ],
          )
      if res.component.label == "Remove Premium :(":
          db.update_one({'guild_id': ctx.guild.id}, {'$set': {'premium': 'False'}})
          await res.respond(
            type=InteractionType.ChannelMessageWithSource,
            content=f'Premium Has Been Removed From, {ctx.guild.name}'
          )
          await m.edit(
            "Would you like to add or remove premium from this guild?",
            components=[
              Button(style=ButtonStyle.green, label="Add Premium :)", disabled=True, emoji="➕"),
              Button(style=ButtonStyle.red, label="Remove Premium :(", disabled=True, emoji="➖"),
            ],
          )
    except asyncio.TimeoutError:
        await m.edit(
            "⏲️ Time ran out. You took too long to respond!",
            components=[
                Button(style=ButtonStyle.red, label="Expired", emoji="✖️", disabled=True),
            ],
        )



@client.command(description="owner command", usage="hostinfo")
@commands.is_owner()
async def hostinfo(ctx):
  import psutil
  cpu_per = round(psutil.cpu_percent(),1)
  mem_per = round(psutil.virtual_memory().percent,1)
  disk_per = round(psutil.disk_usage('/').percent,1)
  uname = platform.uname()
  embed = discord.Embed(description=f"""```asciidoc\n==  VPS HOST INFORMATION  ==
 System    :: {uname.system}-{uname.processor}
 Node Name :: {uname.node}
 Version   :: {uname.version}
 Memory    :: {mem_per}%
 CPU       :: {cpu_per}%
 Disk      :: {disk_per}%
 Network   :: N/A%
```""")
  await ctx.send(embed=embed)


@client.command()
@commands.is_owner()
async def pbi(ctx):
    avatar = client.user.avatar_url if client.user.avatar else client.user.default_avatar_url
    users = len(set(client.get_all_members()))
    servers = (len(client.guilds))
    s=discord.Embed(colour=discord.Colour.random())
    s.add_field(name="Servers", value="{}".format(servers))
    s.add_field(name="Users", value="{}".format(users))
    s.add_field(name="Shards", value="{}/{}".format(ctx.guild.shard_id + 1, client.shard_count))
    s.set_author(name="private beta info", icon_url=avatar)
    await ctx.send(embed=s)

@client.command()
@commands.is_owner()
async def pbsi(ctx):
    s=discord.Embed(colour=discord.Colour.random())
    servers = client.guilds
    for x in range(client.shard_count):
        if x == ctx.guild.shard_id:
            guildshard = ""
        else:
            guildshard = ""
    for shard in list(client.shards):
        if client.get_shard(shard).is_closed:
            sstatus = f"DISCONNECTED"
            break
        if client.get_shard(shard).is_ws_ratelimited:
            sstatus = f"RATELIMITED"
            break
        if not client.get_shard(shard).is_ws_ratelimited and not client.get_shard(shard).is_closed:
            sstatus = f"CONNECTED"
            break
    s.add_field(name="<:online:857840298196729917> {} Shard {}".format(guildshard, x + 1), value=f"```\nPing     : {round(client.latencies[x][1]*1000)}ms.\nServers  : {len([guild for guild in servers if guild.shard_id == x])}\nUsers    : {sum([guild.member_count for guild in servers if guild.shard_id == x])}\nStatus   : {sstatus}```")
    s.set_footer(text=f"Current Shard: {ctx.guild.shard_id + 1}")
    s.set_author(name="private beta info", icon_url=client.user.avatar_url if client.user.avatar else client.user.default_avatar_url)
    await ctx.send(embed=s)



@client.event
async def on_message(message):
    try:
      extras = db.find_one({'guild_id': message.guild.id})["prefix"]
    except:
      extras = "%"
    if message.content.lower() == "<@!771568117180268584>":
      await message.add_reaction('<a:r_pinged:866568105480028160>')
    if message.content.lower() == "<@!771568117180268584>" or message.content.lower() in ("refuge", "yo refuge", "wheres refuge", "where's refuge", "bro refuge", "ay refuge", "refuge wyd"): # eventually let me make a txt file or [] full of response things for this
        try:
            await message.reply(embed=create_embed(f"Hello! I am refuge. I was created by Saiv. For a list of my commands, type: `" + ' and '.join(extras) + "help`!"))
        except:
            try:
                await message.reply(f"(Missing Permission ~ `Embed Links`)\nHello! I am refuge. I was created by Saiv. For a list of my commands, type: `" + ' and '.join(extras) + "help`!")
            except:
                pass
            #print(f"{Fore.RED}[Status @ {datetime.fromtimestamp(time.time()).strftime('%H:%M:%S')}] {e}{Fore.RESET}")
    await client.process_commands(message)



@client.command()
async def forcestop(ctx):
  if commands.is_owner or ctx.author.id == "750507937746649159":
    os._exit(0)

@tasks.loop(hours=24, reconnect=True)
async def bot_restart():
    try:
        channel = client.get_channel(int(os.environ.get('ONLINE_CHANNEL_ID')))
        await channel.edit(name="🟡")
    except:
        pass
    await client.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.playing, name=f"Restarting By Default.."))
    os._exit(0)

print(Fore.CYAN + "\n=======================\n" + Fore.RESET)
client.run(os.environ.get('BOT_TOKEN'), reconnect=True)