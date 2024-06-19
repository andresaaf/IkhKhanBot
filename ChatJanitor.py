from IFeature import IFeature
import discord
from itertools import zip_longest
from six.moves import urllib
from bs4 import BeautifulSoup

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
                'permissions' : [ discord.Permissions.manage_messages ],
                'parameters' : [ OptionalArg(int, 1) ],
                'func' : self.purge
            },
            '.reactw' : {
                'usage' : '.reactw <word> [prev_msg=1]',
                'parameters' : [ str, OptionalArg(int, 1) ],
                'func' : self.reactw
            },
            'MAT' : {
                'usage' : 'MAT',
                'parameters' : [],
                'func' : self.mat
            }
        }

    async def on_message(self, message):
        msg = message.content.split(' ')
        if msg[0] in self.cmds:
            cmd = self.cmds[msg[0]]
            user_permissions = message.channel.permissions_for(message.author)
            if 'permissions' in cmd and not all((user_permissions & perm) for perm in cmd['permissions']):
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

    async def mat(self, message):
        message = await message.channel.send(embed=self.mat_plz())
        await message.add_reaction("🔄")
        await message.add_reaction("🌿")

    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return
        if reaction.message.author.id == self.client.user.id and len(reaction.message.embeds) == 1:
            if reaction.message.embeds[0].title == "Du kan väl för fan laga lite":
                await reaction.remove(user)

                if reaction.emoji == "🔄": # Refresh
                    vego = not any([True for react in reaction.message.reactions if react.emoji == "🌿"])
                    await reaction.message.edit(embed=self.mat_plz(vego))
                elif reaction.emoji == "🌿": # vego
                    await reaction.message.edit(embed=self.mat_plz(True))
                    await reaction.message.remove_reaction("🌿", self.client.user)
                    await reaction.message.add_reaction("🍖")
                elif reaction.emoji == "🍖": # MEAT
                    await reaction.message.edit(embed=self.mat_plz(False))
                    await reaction.message.remove_reaction("🍖", self.client.user)
                    await reaction.message.add_reaction("🌿")
                else:
                    pass

    def mat_plz(self, vego=False):
        url = "https://vadfanskajaglagatillmiddag.nu/" + ("vegetariskt" if vego else "")
        read = BeautifulSoup(urllib.request.urlopen(url).read(), "html.parser")
        mat = read.body.find('div', attrs={'class':'wpb_content_element'}).find('a')
        embed = discord.Embed(
                title="Du kan väl för fan laga lite",
                description=f"[{mat.text}]({mat.get('href')})",
                color=0xf09767
            )
        embed.set_author(name="🌿" if vego else "🍖")
        return embed
