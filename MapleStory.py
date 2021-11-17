from IFeature import IFeature
import discord

import os
import time
import asyncio
import requests
import functools
import urllib3


class MapleStory(IFeature):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_message(self, message):
        msg = message.content.split(' ')
        if len(msg) > 1 and msg[0] == '.maple':
            await message.delete()

            if msg[1] == 'maintenance':
                await self.check_maintenance(message.channel)

    async def check_maintenance(self, channel):
        checker = MaintenanceCheck()
        emb = discord.Embed(
            title="EMS Reboot",
            description="Checking connection...",
            color=0xE67E22
        )
        msg = await channel.send(None, embed=emb)
        while not await checker.check(MaintenanceCheck.servers['EMS']['Reboot'][0]):
            emb.color=0xE74C3C
            emb.description="Offline"
            await msg.edit(embed=emb)
            await asyncio.sleep(10)
        
        emb.color=0x2ECC71
        emb.description="Online"
        await msg.edit(embed=emb)
        await channel.send(f"@here EMS Reboot is back up!")

class MaintenanceCheck:
    servers = {
        'EMS': {
            'Login': [{
                'name': 'Login',
                'address': '18.196.14.103',
                'port': '8484'
            }],
            'Reboot': [{
                'name' : 'Channel 1',
                'address' : '8.31.99.161',
                'port' : '8585'
            }],
        },
    }

    def __init__(self):
        pass

    async def check(self, server):
        try:
            future1 = asyncio.get_event_loop().run_in_executor(None, functools.partial(requests.get, data={
                'timeout': 5
            }), f"http://{server['address']}:{server['port']}")
            await future1
        except Exception as ex:
            if type(ex) == requests.exceptions.ConnectTimeout or type(ex.args[0]) == urllib3.exceptions.MaxRetryError:
                return False
        return True

