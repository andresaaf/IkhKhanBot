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
        rollers = [[user, [random.randint(1, 100)]] for user in userlist] # [[user, [roll, roll...]], ...]
        max_roll = 0
        num_active = 0

        def update():
            nonlocal max_roll
            nonlocal num_active
            num_active = 0
            max_roll = 0
            for roller in rollers:
                roll = roller[1][-1]
                if roll > max_roll:
                    max_roll = roll
                    num_active = 1
                elif roll == max_roll:
                    num_active += 1

        update()

        roll_cnt = 1

        while num_active > 1:
            for roller in rollers:
                if len(roller[1]) == roll_cnt and roller[1][-1] == max_roll:
                    roller[1].append(random.randint(1, 100))
            roll_cnt += 1
            update()

        winner = None
        for roller in rollers:
            if len(roller[1]) == roll_cnt and roller[1][-1] == max_roll:
                winner = roller
                break
        assert(winner is not None)

        descr = ""
        for user, rolls in rollers:
            for roll in rolls[:-1]:
                descr += f"~~{roll}~~ "
            descr += f"**{rolls[-1]}**\t{user.mention}\n"
        
        descr += f"\nWinner winner chicker dinner: {winner[0].mention}"
        
        embed = discord.Embed(
                title="GAMBA ROLL",
                description=descr,
            )
        return embed
