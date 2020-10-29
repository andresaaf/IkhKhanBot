from IFeature import IFeature
import discord

class AudioPlayer(IFeature):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def cleanup(self):
        pass

    async def on_ready(self):
        pass

    async def on_message(self, message):
        pass

    class Song:
        pass

    class Queue:
        pass