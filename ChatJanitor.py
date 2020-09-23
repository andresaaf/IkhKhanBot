from IFeature import IFeature
import discord

class ChatJanitor(IFeature):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cmds = {
            '.purge' : {
                'usage' : '.purge <no_lines>',
                'permissions' : [ 'manage_messages' ],
                'parameters' : 1,
                'func' : self.purge
            },
        }

    async def on_message(self, message):
        msg = message.content.split(' ')
        if msg[0] in self.cmds:
            cmd = self.cmds[msg[0]]
            if 'permissions' in cmd and not all(getattr(message.author.permissions_in(message.channel), perm) for perm in cmd['permissions']):
                await message.author.send("No permissions")
                await message.delete()
                return
            
            if 'roles' in cmd:
                roles = filter(lambda role: role.name in cmd['roles'], message.author.roles)
                if not all(role.name in cmd['roles'] for role in roles):
                    await message.author.send("No role")
                    await message.delete()
                    return

            if 'parameters' in cmd:
                if type(cmd['parameters']) is int:
                    if len(msg) - 1 < cmd['parameters']:
                        await message.author.send(f"Usage: {cmd['usage']}")
                        await message.delete()
                        return
                else:
                    if cmd['parameters']['min'] < (len(msg) - 1) < cmd['parameters']['max']:
                        await message.author.send(f"Usage: {cmd['usage']}")
                        await message.delete()
                        return

            await cmd['func'](message, msg[1:])
    
    async def purge(self, message, msg):
        try:
            lines = int(msg[0])
        except:
            await message.author.send("Usage: .purge <no_lines>")
            await message.delete()
            return
        await message.channel.purge(limit=lines+1)
