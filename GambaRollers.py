from IFeature import IFeature
import discord

import random

class GambaRollers(IFeature):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_message(self, message):
        async def usage():
            await message.author.send("Usage: .roll [max|min-max|@user1 @user2...]")

        async def send_roll(embed):
            await message.channel.send(embed=embed)

        msg = message.content.split(' ')
        if len(msg) > 0 and msg[0] == '.roll':
            await message.delete()

            # .roll - Roll 1-100
            if len(msg) == 1:
                await send_roll(self.roll(message.author.mention, 1, 100))

            # .roll max | .roll min-max
            elif len(msg) == 2:
                minmax = msg[1].split('-')
                if len(minmax) == 1:
                    if msg[1].isdigit() and int(msg[1]) > 1:
                        await send_roll(self.roll(message.author.mention, 1, int(msg[1])))
                    else:
                        await usage()
                elif len(minmax) == 2:
                    if minmax[0].isdigit() and minmax[1].isdigit() and int(minmax[0]) < int(minmax[1]):
                        await send_roll(self.roll(message.author.mention, int(minmax[0]), int(minmax[1])))
                    else:
                        await usage()
                else:
                    await usage()
            else:
                if len(message.mentions) > 1:
                    await send_roll(self.user_roll(message.mentions))
                else:
                    await usage()

    def roll(self, user, vmin, vmax):
        embed = discord.Embed(
                title=f"GAMBA ROLL {vmin}-{vmax}",
                description=f"{random.randint(vmin, vmax)}\t{user}",
            )
        return embed

    def user_roll(self, userlist):
        rolls = []
        descr = ""
        winner = None
        max_roll = 0
        for user in userlist:
            roll = random.randint(1, 100)
            while roll in rolls:
                roll = random.randint(1, 100)
            if roll > max_roll:
                max_roll = roll
                winner = user
            rolls.append(roll)
            descr += f"{roll}\t{user.mention}\n"
        
        descr += f"\nWinner winner chicker dinner: {winner.mention}"
        
        embed = discord.Embed(
                title="GAMBA ROLL",
                description=descr,
            )
        return embed
