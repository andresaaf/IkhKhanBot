from IFeature import IFeature
import discord

class ReactForRoles(IFeature):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def cleanup(self):
        pass

    async def on_ready(self):
        pass
        # TODO: Load from database
        #self.category = discord.utils.find(lambda ch: ch.name == "SHIT", self.client.guilds[0].categories)
        #self.channel = discord.utils.find(lambda ch: ch.name == "roles", self.category.text_channels)

    async def on_reaction_add(self, reaction, user):
        pass

    async def on_reaction_remove(self, reaction, user):
        pass