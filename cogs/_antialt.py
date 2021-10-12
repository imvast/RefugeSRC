import discord
import json
import numpy as np
import random
import string
import Augmentor
import os
import shutil
import asyncio
import time
import pymongo

from discord.ext import commands
from discord.utils import get

from PIL import ImageFont, ImageDraw, Image

from Utils.utils import utils


# Connect to MongoDB
mongoClient = pymongo.MongoClient(os.environ.get('BOT_DB'))
db = mongoClient.get_database("refuge").get_collection("server-data")
db2 = mongoClient['refuge']
antitoggle = db2['antitoggle']
blacklist = db2['blacklist']
gprefix = db['prefix']
limits = db2['limits']

# ------------------------ COGS ------------------------ #  

class OnJoinCog(commands.Cog, name="on join"):
    def __init__(self, bot):
        self.bot = bot

# ------------------------------------------------------ #  

    @commands.Cog.listener()
    async def on_member_join(self, member):

        if (member.bot):
            return
        minaccdate = 604800 # 7 days
        captchacheck = False
        logsChannel = db.find_one({ "guild_id": member.guild.id })["logs_channel"]
        logChannel = self.bot.get_channel(logsChannel)
        captchaChannel = self.bot.get_channel(logsChannel)

        memberTime = f"{member.joined_at.year}-{member.joined_at.month}-{member.joined_at.day} {member.joined_at.hour}:{member.joined_at.minute}:{member.joined_at.second}"

        if captchacheck is False:
            userAccountDate = member.created_at.timestamp()
            print(userAccountDate)
            if userAccountDate < minaccdate:
                minAccountDate = minaccdate / 3600
                embed = discord.Embed(title = f"**YOU HAVE BEEN KICKED FROM {member.guild.name}**", description = f"Reason : Your account is more young that the server limit ({minAccountDate} hours).", color = 0xff0000)
                await member.send(embed = embed)
                await member.kick(reason="[refuge altidentifier] + Account Too Young. (Anti-Alt)") # Kick the user
                # Logs
                embed = discord.Embed(title = f"**{member} has been kicked.**", description = f"**Reason :** Account age is younger than the server limit of, `{minAccountDate}` hours\n\n**__User informations :__**\n\n**Name :** {member}\n**ID :** {member.id}\n**Account creation :** {member.created_at}", color = 0xff0000)
                embed.set_footer(text= f"at {member.joined_at}")
                await logChannel.send(embed=embed)

        if False is True:#db["captcha"] is True:
            
            # Give temporary role
            getrole = get(member.guild.roles, id = db["temporaryRole"])
            await member.add_roles(getrole)
            
            # Create captcha
            image = np.zeros(shape= (100, 350, 3), dtype= np.uint8)

            # Create image 
            image = Image.fromarray(image+255) # +255 : black to white

            # Add text
            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype(font= "Tools/arial.ttf", size= 60)

            text = ' '.join(random.choice(string.ascii_uppercase) for _ in range(6)) # + string.ascii_lowercase + string.digits

            # Center the text
            W, H = (350,100)
            w, h = draw.textsize(text, font= font)
            draw.text(((W-w)/2,(H-h)/2), text, font= font, fill= (90, 90, 90))

            # Save
            ID = member.id
            folderPath = f"captchaFolder/captcha_{ID}"
            try:
                os.mkdir(folderPath)
            except:
                if os.path.isdir('captchaFolder') is False:
                    os.mkdir("captchaFolder")
                if os.path.isdir(folderPath) is True:
                    shutil.rmtree(folderPath)
                os.mkdir(folderPath)
            image.save(f"{folderPath}/captcha{ID}.png")

            # Deform
            p = Augmentor.Pipeline(folderPath)
            p.random_distortion(probability=1, grid_width=4, grid_height=4, magnitude=14)
            p.process()

            # Search file in folder
            path = f"{folderPath}/output"
            files = os.listdir(path)
            captchaName = [i for i in files if i.endswith('.png')]
            captchaName = captchaName[0]

            image = Image.open(f"{folderPath}/output/{captchaName}")
            
            # Add line
            width = random.randrange(6, 8)
            co1 = random.randrange(0, 75)
            co3 = random.randrange(275, 350)
            co2 = random.randrange(40, 65)
            co4 = random.randrange(40, 65)
            draw = ImageDraw.Draw(image)
            draw.line([(co1, co2), (co3, co4)], width= width, fill= (90, 90, 90))
            
            # Add noise
            noisePercentage = 0.25 # 25%

            pixels = image.load() # create the pixel map
            for i in range(image.size[0]): # for every pixel:
                for j in range(image.size[1]):
                    rdn = random.random() # Give a random %
                    if rdn < noisePercentage:
                        pixels[i,j] = (90, 90, 90)

            # Save
            image.save(f"{folderPath}/output/{captchaName}_2.png")

            # Send captcha
            captchaFile = discord.File(f"{folderPath}/output/{captchaName}_2.png")
            captchaEmbed = await captchaChannel.send(f"**YOU MUST PASS THE CAPTCHA TO ENTER IN THE SERVER :**\nPlease {member.mention}, enter the captcha to get access to the whole serveur (only 6 uppercase letters).", file= captchaFile)
            # Remove captcha folder
            try:
                shutil.rmtree(folderPath)
            except Exception as error:
                print(f"Delete captcha file failed {error}")

            # Check if it is the right user
            def check(message):
                if message.author == member and  message.content != "":
                    return message.content

            try:
                msg = await self.bot.wait_for('message', timeout=120.0, check=check)
                # Check the captcha
                password = text.split(" ")
                password = "".join(password)
                if msg.content == password:

                    embed = discord.Embed(description=f"{member.mention} passed the captcha.", color=0x2fa737) # Green
                    await captchaChannel.send(embed = embed, delete_after = 5)
                    # Give and remove roles
                    try:
                        getrole = get(member.guild.roles, id = db["roleGivenAfterCaptcha"])
                        if getrole is not False:
                            await member.add_roles(getrole)
                    except Exception as error:
                        print(f"Give and remove roles failed : {error}")
                    try:
                        getrole = get(member.guild.roles, id = db["temporaryRole"])
                        await member.remove_roles(getrole)
                    except Exception as error:
                        print(f"No temp role found (onJoin) : {error}")
                    time.sleep(3)
                    await captchaEmbed.delete()
                    await msg.delete()
                    # Logs
                    embed = discord.Embed(title = f"**{member} passed the captcha.**", description = f"**__User informations :__**\n\n**Name :** {member}\n**Id :** {member.id}", color = 0x2fa737)
                    embed.set_footer(text= f"at {memberTime}")
                    await utils.sendLogMessage(self, event=member, channel=logsChannel, embed=embed)

                else:
                    link = await captchaChannel.create_invite(max_age=172800) # Create an invite
                    embed = discord.Embed(description=f"{member.mention} failed the captcha.", color=0xca1616) # Red
                    await captchaChannel.send(embed = embed, delete_after = 5)
                    embed = discord.Embed(title = f"**YOU HAVE BEEN KICKED FROM {member.guild.name}**", description = f"Reason : You failed the captcha.\nServer link : <{link}>", color = 0xff0000)
                    await member.send(embed = embed)
                    await member.kick() # Kick the user
                    time.sleep(3)
                    await captchaEmbed.delete()
                    await msg.delete()
                    # Logs
                    embed = discord.Embed(title = f"**{member} has been kicked.**", description = f"**Reason :** He failed the captcha.\n\n**__User informations :__**\n\n**Name :** {member}\n**Id :** {member.id}", color = 0xff0000)
                    embed.set_footer(text= f"at {memberTime}")
                    await utils.sendLogMessage(self, event=member, channel=logsChannel, embed=embed)

            except (asyncio.TimeoutError):
                link = await captchaChannel.create_invite(max_age=172800) # Create an invite
                embed = discord.Embed(title = f"**TIME IS OUT**", description = f"{member.mention} has exceeded the response time (120s).", color = 0xff0000)
                await captchaChannel.send(embed = embed, delete_after = 5)
                try:
                    embed = discord.Embed(title = f"**YOU HAVE BEEN KICKED FROM {member.guild.name}**", description = f"Reason : You exceeded the captcha response time (120s).\nServer link : <{link}>", color = 0xff0000)
                    await member.send(embed = embed)
                    await member.kick() # Kick the user
                except Exception as error:
                    print(f"Log failed (onJoin) : {error}")
                time.sleep(3)
                await captchaEmbed.delete()
                # Logs
                embed = discord.Embed(title = f"**{member} has been kicked.**", description = f"**Reason :** He exceeded the captcha response time (120s).\n\n**__User informations :__**\n\n**Name :** {member}\n**Id :** {member.id}", color = 0xff0000)
                embed.set_footer(text= f"at {memberTime}")
                await utils.sendLogMessage(self, event=member, channel=logsChannel, embed=embed)

# ------------------------ BOT ------------------------ #  

def setup(bot):
    bot.add_cog(OnJoinCog(bot))