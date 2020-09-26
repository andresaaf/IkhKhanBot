from IFeature import IFeature
import discord
import random

class EventSignup(IFeature):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def cleanup(self):
        pass

    async def on_ready(self):
        pass

    async def on_message(self, message):
        if message.content[0] == ".event":
            if message.content[1] == "create":
                self.create(message.content[2:])

    async def on_reaction_add(self, reaction, user):
        pass

    async def on_reaction_remove(self, reaction, user):
        pass

    async def create(self, args):
        pass