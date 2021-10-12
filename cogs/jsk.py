from jishaku.cog import Jishaku

def setup(client):
    client.add_cog(Jishaku(bot=client))