from discord.ext import commands, tasks
from colorama import Fore as C
import dbl
from discord_webhook import DiscordWebhook, DiscordEmbed

class TopGG(commands.Cog):
    def __init__(self, client):
        self.client = client
        print(f"{C.CYAN}[Status] Cog Loaded: TopGG" + C.RESET)
        self.token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Ijc3MTU2ODExNzE4MDI2ODU4NCIsImJvdCI6dHJ1ZSwiaWF0IjoxNjI2NjY0Mjk3fQ.yg8Nrv4xAckbLjzhrtsniPkYrX_B9klCKAVFv6FyKIg'  # set this to your DBL token
        self.dblpy = dbl.DBLClient(self.client, self.token, webhook_path='/dblwebhook', webhook_auth='password', webhook_port=5000)
        self.update_stats.start()

    @tasks.loop(hours=12)
    async def update_stats(self):
        """This function runs every 2 hours to automatically update the server count on top.gg."""
        await self.client.wait_until_ready()
        if str(self.client.user.id) == str("771568117180268584"):
            try:
                server_count = len(self.client.guilds)
                await self.dblpy.post_guild_count(server_count)
                print('[Status] TopGG: Posted server count ({})'.format(server_count))
            except Exception as e:
                print('[Status] TopGG: Failed to post server count\n{}: {}'.format(type(e).__name__, e))
        else:
            print(f'[Status] TopGG: Stopped. ({self.client.user.id})')
            self.update_stats.cancel()

    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        """An event that is called whenever someone votes for the bot on top.gg."""
        print("Received an upvote:", "\n", data, sep="")
        webhook = DiscordWebhook(url="https://discord.com/api/webhooks/857763562104553473/ZPpXqG8jhcQOIoFz5E4ROJivKb8i_VXhyWlsDa4ZduB2KsL9ZF6NGIFMpJp5J8kmlJkY")
        log = DiscordEmbed(title = f"Upvote Recieved", description = str(data))
        webhook.add_embed(log); webhook.execute()

    @commands.Cog.listener()
    async def on_dbl_test(self, data):
        """An event that is called whenever someone tests the webhook system for your bot on top.gg."""
        print("Received a test upvote:", "\n", data, sep="")

    @commands.Cog.listener()
    async def on_guild_post(self):
        print("Server count posted successfully")


def setup(bot):
    bot.add_cog(TopGG(bot))