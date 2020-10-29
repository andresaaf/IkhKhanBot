import discord
import asyncio
from Database import Database

from TempVoiceChat import TempVoiceChat
from ChatJanitor import ChatJanitor
from AudioPlayer import AudioPlayer
from EventSignup import EventSignup
#from ReactForRoles import ReactForRoles
from Database import Database

class IKUBot(discord.Client):
    def __init__(self):
        super().__init__()
        self.db = Database()

        self.features = [
            TempVoiceChat(self),
            ChatJanitor(self),
            AudioPlayer(self),
            EventSignup(self),
            #ReactForRoles(self)
        ]

    async def on_ready(self):
        print(f'Connected. Username: {self.user.name} | ID: {self.user.id}')

        for feature in self.features:
            await feature.on_ready()
            print(f"Loaded feature {type(feature).__name__}.")

    async def on_message(self, message):
        if message.author.bot:
            return
        for feature in self.features:
            await feature.on_message(message)

    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        for feature in self.features:
            await feature.on_message_edit(before, after)

    async def on_reaction_add(self, reaction, user):
        for feature in self.features:
            await feature.on_reaction_add(reaction, user)

    async def on_reaction_remove(self, reaction, user):
        for feature in self.features:
            await feature.on_reaction_remove(reaction, user)

    async def on_voice_state_update(self, member, before, after):
        for feature in self.features:
            await feature.on_voice_state_update(member, before, after)

if __name__ == '__main__':
    token = open('token.txt', 'r').readline()
    bot = IKUBot().run(token)