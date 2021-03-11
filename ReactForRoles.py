from IFeature import IFeature
import discord

DB_CREATE = """CREATE TABLE IF NOT EXISTS ReactForRoles (
    guild integer PRIMARY KEY,
    channel integer NOT NULL
);"""

class ReactForRoles(IFeature):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.watch = dict()
        with self.client.db as db:
            db.execute(DB_CREATE)

            db.execute("SELECT guild, channel FROM ReactForRoles")
            for row in db.fetchall():
                self.watch[row[0]] = row[1]

    async def on_message(self, message):
        msg = message.content.split(' ')
        if len(msg) > 1 and msg[0] == '.react':
            await message.delete()

            # TODO: Permission check

            if msg[1] == "add":
                if message.guild.id not in self.watch:
                    await message.author.send("Guild does not have a react for roles set up. .react set in a channel to create it")
                    return
                elif message.channel.id != self.watch[message.guild.id]:
                    await message.author.send("Wrong channel!")
                    return

                if len(msg) != 4 or msg[3][0:3] != "<@&":
                    await message.author.send("Usage: .react add :emote: @role")
                    return
                
                m = await self.find_roles_message(message.channel)
                emb = m.embeds[0]
                descr = self.get_list(emb.description)
                descr.append(f"{msg[2]} - {msg[3]}")

                emb.description = '\n'.join(descr)
                await m.edit(content=None, embed=emb)
                await m.add_reaction(msg[2])
            elif msg[1] == "remove":
                if message.guild.id not in self.watch:
                    await message.author.send("Guild does not have a react for roles set up. .react set in a channel to create it")
                    return
                elif message.channel.id != self.watch[message.guild.id]:
                    await message.author.send("Wrong channel!")
                    return

                if len(msg) != 3:
                    await message.author.send("Usage: .react remove <:emote: or @role>")
                    return
                
                m = await self.find_roles_message(message.channel)
                emb = m.embeds[0]
                descr = self.get_list(emb.description)
                react = None
                for st in descr:
                    if msg[2] in st:
                        react = st.split(' ')[0]
                        descr.remove(st)
                        break

                emb.description = '\n'.join(descr)
                await m.edit(content=None, embed=emb)
                await m.clear_reaction(react)
            elif msg[1] == "set":
                if message.guild.id in self.watch:
                    await message.author.send(f"Guild already has a channel for roles. .react unset to remove it")
                    return

                self.watch[message.guild.id] = message.channel.id
                with self.client.db as db:
                    db.execute("INSERT INTO ReactForRoles (guild, channel) VALUES (?, ?)", (message.guild.id, message.channel.id))
                
                emb = discord.Embed(
                    title="React for roles",
                    description="",
                    color=0xe025f5
                )
                await message.channel.send(None, embed=emb)
            elif msg[1] == "unset":
                if message.guild.id not in self.watch:
                    await message.author.send(f"Guild does not have a channel for roles.")
                    return
                elif self.watch[message.guild.id] != message.channel.id:
                    await message.author.send(f"Write .react unset in the channel with the react for roles message.")
                    return
                
                with self.client.db as db:
                    db.execute("DELETE FROM ReactForRoles WHERE guild = ? AND channel = ?", (message.guild.id, self.watch[message.guild.id]))
                
                m = await self.find_roles_message(message.channel)
                if m is None:
                    del(self.watch[message.guild.id])
                    return

                # TODO: Remove roles?
                await m.delete()
                del(self.watch[message.guild.id])

    async def on_ready(self):
        for guild_id, channel_id in self.watch.items():
            guild = self.client.get_guild(guild_id)
            if not guild:
                print(f"Error! Guild not found: {guild_id}")
                continue

            ch = guild.get_channel(channel_id)
            messages = await ch.history().flatten()
            message = None
            for msg in messages:
                if len(msg.embeds) == 1 and msg.embeds[0].title == "React for roles":
                    message = msg
                    break
            if message is None:
                print(f"Message not found in guild {guild_id}")
                continue

            # TODO: Handle new reacts at startup

    async def parse_react_event(self, payload):
        if payload.channel_id not in self.watch.values():
            return None

        guild = self.client.get_guild(payload.guild_id)
        message = await guild.get_channel(payload.channel_id).fetch_message(payload.message_id)
        if payload.message_id != message.id:
            return None

        user = await guild.fetch_member(payload.user_id)
        descr = self.get_list(message.embeds[0].description)
        react = [x for x in descr if x.startswith(str(payload.emoji))]
        if len(react) == 0:
            await message.remove_reaction(payload.emoji, user)
            return None

        r = int(react[0].split(' - ')[1][3:-1])
        role = [x for x in guild.roles if x.id == r]
        if len(role) == 0:
            print("ERROR!?")
            return None
        return [user, role[0]]
    
    async def on_raw_reaction_add(self, payload):
        event = await self.parse_react_event(payload)
        if event is not None:
            await event[0].add_roles(event[1])

    async def on_raw_reaction_remove(self, payload):
        event = await self.parse_react_event(payload)
        if event is not None:
            await event[0].remove_roles(event[1])

    async def find_roles_message(self, channel):
        async for message in channel.history(limit=200):
            if (message.author == self.client.user
                and len(message.embeds) == 1 and message.embeds[0].title == "React for roles"):
                    return message
        return None

    def get_list(self, descr):
        if descr == discord.Embed.Empty:
            return []
        else:
            return descr.split('\n')