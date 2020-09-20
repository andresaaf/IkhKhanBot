from IFeature import IFeature
import discord
import random

class TempVoiceChat(IFeature):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_names = [
            "Floravägen ASMR",
            "MaintenanceStory",
            "Lönnhistoria",
            "Albins gråthörna",
            "#BLM sometimes when convenient",
            "Robins batongliga",
            "Nickes snarkhörna",
            "Albins snarkhörna",
            "Sommaranalen",
            "Willes AFK & Alkoholism",
            "Anonyma Kitavaister"
        ]

    async def cleanup(self):
        pass

    async def on_ready(self):
        self.category = discord.utils.find(lambda ch: ch.name == "Temp", self.client.guilds[0].categories)
        self.create_channel = discord.utils.find(lambda ch: ch.name == "New Temp Channel", self.category.voice_channels)
        await self.remove_unused_channels()
        for member in self.create_channel.members:
            await self.create_temp_voice(member)

    async def on_voice_state_update(self, member, before, after):
        if after.channel == self.create_channel:
            await self.create_temp_voice(member)
        if before.channel.category == self.category and before.channel != self.create_channel:
            if len(before.channel.members) == 0:
                await before.channel.delete()

    async def create_temp_voice(self, member):
        new_channel = await self.category.create_voice_channel(f"{self.channel_names[random.randrange(0, len(self.channel_names))]}") # #{channel}
        await member.move_to(new_channel)

    async def remove_unused_channels(self):
        for ch in filter(lambda channel: channel != self.create_channel, self.category.voice_channels):
            if len(ch.members) == 0:
                await ch.delete()
