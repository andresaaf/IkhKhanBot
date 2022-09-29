from IFeature import IFeature
import discord

import calendar
import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

DB_CREATE = """CREATE TABLE IF NOT EXISTS MapleReminder (
    guild integer PRIMARY KEY,
    channel integer NOT NULL
);"""

class MapleStory(IFeature):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        self.skip_once = False
        self.watch = dict()
        with self.client.db as db:
            db.execute(DB_CREATE)

            db.execute("SELECT guild, channel FROM MapleReminder")
            for row in db.fetchall():
                self.watch[row[0]] = row[1]

        # Start shceduler
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_job(self.run_end_of_month_check, IntervalTrigger(seconds=50))
        self.scheduler.start()

    async def on_message(self, message):
        msg = message.content.split(' ')
        if msg[0] == '.maple':
            if msg[1] == 'set_totem_channel':
                self.watch[message.guild.id] = message.channel.id
                with self.client.db as db:
                    try:
                        db.execute("INSERT INTO MapleReminder (guild, channel) VALUES (?, ?)", (message.guild.id, message.channel.id))
                    except:
                        pass
                await message.author.send("Registered channel")
                await message.delete()
            elif msg[1] == 'remove_totem_channel':
                with self.client.db as db:
                    try:
                        db.execute("DELETE FROM MapleReminder WHERE guild = ? AND channel = ?", (message.guild.id, self.watch[message.guild.id]))
                    except:
                        pass
                await message.author.send("Removed channel")
                await message.delete()

    async def run_end_of_month_check(self):
        if self.skip_once:
            self.skip_once = False
            return

        # Last day of month?
        now = datetime.datetime.now()
        if now.day == calendar.monthrange(now.year, now.month)[1]:
            # Fire at 12:00 and 18:00
            if now.minute == 0 and (now.hour == 12 or now.hour == 20):
                self.skip_once = True
                for guild, channel in self.watch.items():
                    try:
                        await self.client.get_guild(guild).get_channel(channel).send("@everyone Don't forget to buy your totems! Last day")
                    except:
                        pass
