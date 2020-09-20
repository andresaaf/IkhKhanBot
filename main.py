import discord
import asyncio

from TempVoiceChat import TempVoiceChat
from ChatJanitor import ChatJanitor

class IKUBot(discord.Client):
    def __init__(self):
        super().__init__()
        self.features = []

    async def on_ready(self):
        print(f'Connected. Username: {self.user.name} | ID: {self.user.id}')
        self.features = [
            TempVoiceChat(self),
            ChatJanitor(self)
        ]
        for feature in self.features:
            await feature.on_ready()

    async def on_message(self, message):
        if message.author.bot:
            return
        for feature in self.features:
            await feature.on_message(message)

    async def on_reaction_add(self, reaction, user):
        #print(f"Reaction {reaction} from {user}")
        for feature in self.features:
            await feature.on_reaction_add(reaction, user)

    async def on_reaction_remove(self, reaction, user):
        #print(f"Reaction removed {reaction} from {user}")
        for feature in self.features:
            await feature.on_reaction_remove(reaction, user)

    async def on_voice_state_update(self, member, before, after):
        #print(f"{member} went from {before} to {after}")
        for feature in self.features:
            await feature.on_voice_state_update(member, before, after)

if __name__ == '__main__':
    token = open('token.txt', 'r').readline()
    bot = IKUBot().run(token)