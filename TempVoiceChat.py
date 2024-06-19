from IFeature import IFeature
import discord
import random

# TODO: Remove monitor?
DB_CREATE = """CREATE TABLE IF NOT EXISTS TempVoiceChat (
    guild integer PRIMARY KEY,
    category integer NOT NULL,
    monitor integer NOT NULL
);"""

DB_CREATE_NAMES = """CREATE TABLE IF NOT EXISTS TempVoiceChat_Names (
    guild integer NOT NULL,
    name text NOT NULL,
    unique (guild, name)
);"""

class TempVoiceChat(IFeature):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        with self.client.db as db:
            db.execute(DB_CREATE)
            db.execute(DB_CREATE_NAMES)

            db.execute("SELECT guild, category, monitor FROM TempVoiceChat")
            self.monitor_channels = { row[0] : [row[1], row[2]] for row in db.fetchall() }

            db.execute("SELECT guild, name FROM TempVoiceChat_Names")
            self.names = { g : [] for g in self.monitor_channels.keys() }
            for row in db.fetchall():
                self.names[row[0]] = [row[1]] + (self.names[row[0]] or [])

    async def cleanup(self):
        pass

    async def on_message(self, message):
        msg = message.content.split(' ')
        if len(msg) > 1 and msg[0] == '.voice':
            # Check permission
            user_permissions = message.channel.permissions_for(message.author)
            if not user_permissions.manage_messages:
                await message.author.send("No permission")
                return

            if msg[1] == 'set':
                if len(msg) < 3:
                    await message.author.send("Usage: .voice set <category name>")
                    return
                category_name = (" ".join(msg[2:])).strip(' \t\r\n')
                print(message.guild.categories)
                if not any(cat for cat in message.guild.categories if cat.name == category_name):
                    await message.author.send("Category not found! Create it and run the command again")
                    return
                category = next(c for c in message.guild.categories if c.name == category_name)
                if len(category.voice_channels) == 0:
                    monitor = await category.create_voice_channel("New Temp Channel", bitrate=category.guild.bitrate_limit)
                else:
                    monitor = category.voice_channels[0]
                with self.client.db as db:
                    # TODO: Insert or replace?
                    db.execute("SELECT guild, category, monitor FROM TempVoiceChat WHERE guild = ?", (message.guild.id,))
                    if db.fetchone() is None:
                        db.execute("INSERT INTO TempVoiceChat (guild, category, monitor) VALUES (?, ?, ?)", (message.guild.id, category.id, monitor.id))
                        self.names[message.guild.id] = []
                    else:
                        db.execute("UPDATE TempVoiceChat SET category = ?, monitor = ? WHERE guild = ?", (category.id, monitor.id, message.guild.id))
                self.monitor_channels[message.guild.id] = [category.id, monitor.id]
            elif msg[1] == 'add':
                if len(msg) < 3:
                    await message.author.send("Usage: .voice add <temp channel name>")
                    return
                name = (" ".join(msg[2:])).strip(' \t\r\n')
                with self.client.db as db:
                    db.execute("INSERT INTO TempVoiceChat_Names ('guild', 'name') VALUES (?, ?)", (message.guild.id, name))
                self.names[message.guild.id].append(name)
            elif msg[1] == 'remove':
                if len(msg) < 3:
                    await message.author.send("Usage: .voice remove <temp channel name>")
                    return
                name = (" ".join(msg[2:])).strip(' \t\r\n')
                with self.client.db as db:
                    db.execute("DELETE FROM TempVoiceChat_Names WHERE guild = ? AND name = ?", (message.guild.id, name))
                self.names[message.guild.id].remove(name)
            elif msg[1] == 'list':
                if len(self.names[message.guild.id]) > 0:
                    await message.author.send("Name list:\n" + "\n".join(self.names[message.guild.id]))
                else:
                    await message.author.send("No channel names added.")

    async def on_ready(self):
        for guild_id, channel in self.monitor_channels.items():
            if any(g for g in self.client.guilds if g.id == guild_id):
                g = next(g for g in self.client.guilds if g.id == guild_id)
                category = g.get_channel(channel[0])
                monitor_channel = g.get_channel(channel[1])
                await self.remove_unused_channels(category, monitor_channel)
                for member in monitor_channel.members:
                    await self.create_temp_voice(category, member)
            else:
                print(f"Guild not found: {guild_id}. Monitor channel: {channel}")

    async def on_voice_state_update(self, member, before, after):
        if after.channel is not None and after.channel.guild.id in self.monitor_channels:
            monitor_channel = self.monitor_channels[after.channel.guild.id][1]
            if after.channel.id == monitor_channel:
                new_channel = await self.create_temp_voice(after.channel.category, member)
                await self.client.wait_for('voice_state_update', check=lambda _1,_2,_3: len(new_channel.members) == 0)
                await new_channel.delete()

    async def create_temp_voice(self, category, member):
        if len(self.names[category.guild.id]) > 0:
            channel_name = f"{self.names[category.guild.id][random.randrange(0, len(self.names[category.guild.id]))]}"
            new_channel = await category.create_voice_channel(channel_name, bitrate=category.guild.bitrate_limit)
            await member.move_to(new_channel)
            return new_channel
        return None

    async def remove_unused_channels(self, category, monitor_channel):
        for ch in filter(lambda channel: channel != monitor_channel, category.voice_channels):
            if len(ch.members) == 0:
                await ch.delete()
