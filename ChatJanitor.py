from IFeature import IFeature
import discord
from itertools import zip_longest

class OptionalArg:
    def __init__(self, T, default):
        self.T = T
        self.default = default

    def __call__(self, arg):
        return self.default if arg is None else self.T(arg)

class ChatJanitor(IFeature):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cmds = {
            '.purge' : {
                'usage' : '.purge [no_lines=1]',
                'permissions' : [ 'manage_messages' ],
                'parameters' : [ OptionalArg(int, 1) ],
                'func' : self.purge
            },
            '.reactw' : {
                'usage' : '.reactw <word> [prev_msg=1]',
                'parameters' : [ str, OptionalArg(int, 1) ],
                'func' : self.reactw
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
                    await message.author.send("No permissions")
                    await message.delete()
                    return

            args = []
            if 'parameters' in cmd:
                param_zip = zip_longest(msg[1:], cmd['parameters'])
                try:
                    for arg, param in param_zip:
                        if type(param) is not OptionalArg and arg is None:
                            raise Exception()
                        args.append(param(arg))
                except:
                    await message.author.send(f"Usage: {cmd['usage']}")
                    await message.delete()
                    return
            await cmd['func'](message, *args)
    
    async def purge(self, message, lim):
        await message.channel.purge(limit=lim+1)

    async def reactw(self, message, word, msg_offset):
        if not all(c.upper() >= 'A' and c.upper() <= 'Z' for c in word):
            await message.author.send(f"Word has to be [A-Z]+")
            await message.delete()
            return
        history = await message.channel.history(limit=msg_offset+1).flatten()
        if len(history) <= 1:
            await message.delete()
            return
        await message.delete()
        react_msg = history[msg_offset]
        A = ord('\U0001F1E6')
        for char in word:
            await react_msg.add_reaction(chr(A + (ord(char.upper()) - ord('A'))))