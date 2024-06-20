from IFeature import IFeature
import discord
from discord.ext import tasks
import threading
import socket
import datetime

DB_CREATE = """CREATE TABLE IF NOT EXISTS MapleStory (
    guild integer PRIMARY KEY,
    channel integer NOT NULL,
    role integer NOT NULL
);"""

maple_mvps = []
MAX_FILE_SIZE = 32768

def recv_thread():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serversocket:
        serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serversocket.bind(('0.0.0.0', 8089))
        serversocket.listen()
        while True:
            conn, addr = serversocket.accept()
            buf = ""
            with conn:
                conn.settimeout(5.0)
                try:
                    buf = conn.recv(1024)
                    imgbuf = bytes()
                    recv = conn.recv(4096)
                    while len(recv) > 0 and len(imgbuf) < MAX_FILE_SIZE:
                        imgbuf += recv
                        recv = conn.recv(4096)
                    file = open('mvp/mvp.png', 'wb')
                    file.write(imgbuf)
                    file.close()
                except Exception as ex:
                    print(ex)
                conn.close()
            if len(buf) > 0:
                buf = buf.decode()
                maple_mvps.append(buf)

class MapleStory(IFeature):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.channel = dict()
        with self.client.db as db:
            db.execute(DB_CREATE)

            db.execute("SELECT guild, channel, role FROM MapleStory")
            for row in db.fetchall():
                self.channel[row[0]] = [row[1], row[2]]

        thr = threading.Thread(target=recv_thread)
        thr.start()

    @tasks.loop(seconds=1.0)
    async def loop(self):
        if len(maple_mvps) > 0:
            await self.announce(maple_mvps.pop(0))

    async def on_ready(self):
        self.loop.start()

    async def on_message(self, message):
        msg = message.content.split(' ')
        if msg[0] == '.maple':
            if msg[1] == 'mvp' and len(message.role_mentions) > 0:
                with self.client.db as db:
                    db.execute("INSERT INTO MapleStory (guild, channel, role) VALUES (?, ?, ?)", (message.guild.id, message.channel.id, message.raw_role_mentions[0]))
                self.channel[message.guild.id] = [message.channel.id, message.raw_role_mentions[0]]
                await message.author.send('Done')

    async def announce(self, mvp):
        for g_id, data in self.channel.items():
            guild = self.client.get_guild(g_id)
            if not guild:
                print(f"Maple> Error! Guild not found: {g_id}")
                continue
            ch = guild.get_channel_or_thread(data[0])
            if not ch:
                print(f"Maple> Error! Channel not found: {data[1]}")
                continue
            spl = mvp.split('|')

            file = discord.File('mvp/mvp.png', filename='mvp.png')
            await ch.send(f'<@&{data[1]}> xx:{spl[1]} ch{spl[2]}', file=file)
