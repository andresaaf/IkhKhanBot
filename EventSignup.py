from IFeature import IFeature
import discord
import random
import datetime

class EventSignup(IFeature):
    TEMPLATE_CREATE = ("To create a new event, copy and paste this template here:\n"
                      "> .event create\n"
                      "> @everyone\n"
                      "> Title\n"
                      "> Multi-line Description\n"
                      "> ... that ends with a react:\n"
                      "> \U0001F44D")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.events = list()

    #region Events

    async def cleanup(self):
        pass

    async def on_ready(self):
        pass

    async def on_message(self, message):
        msg = message.content.lstrip(' \t\r\n').split('\n')
        line1 = msg[0].split(' ')
        if line1[0] == ".event":
            if line1[1] == "create":
                if message.guild:
                    await self.init_create(message)
                else:
                    await self.create(message)

    async def on_message_edit(self, before, after):
        for event in self.events:
            if event.template.id == before.id:
                await self.create(after)
                break

    async def on_reaction_add(self, reaction, user):
        for event in self.events:
            if event.message.id == reaction.message.id:
                if reaction.emoji != event.react:
                    await reaction.remove(user)
                    break
                if not user.bot:
                    await event.send()
                break

    async def on_reaction_remove(self, reaction, user):
        for event in self.events:
            if event.message.id == reaction.message.id:
                if reaction.emoji == event.react:
                    await event.send()
                    break

    #endregion Events

    async def init_create(self, message):
        await message.delete()
        self.events.append(EventSignup.Event(channel=message.channel, owner=message.author))
        await message.author.send(self.TEMPLATE_CREATE)

    async def create(self, message):
        event = None
        for ev in reversed(self.events):
            if ev.owner == message.author:
                event = ev
                break
        if event is None:
            await message.author.send("Couldn't find any active event create message for user")
            return
        
        event.template = message
        msg = message.content.split('\n')[1:] # Trim first line

        # Remove potential > in message lines
        msg = list(map(lambda line: line.lstrip('> '), msg))
                
        # Parse
        event.mentions = msg[0]
        event.title = msg[1]
        event.descr = '\n'.join(msg[2:len(msg)-1])
        event.react = msg[-1]

        await event.send()

    class Event:
        def __init__(self, **kwargs):
            self.template = None # DM message to detect changes
            self.channel = kwargs.get('channel', None) # Channel to send event to
            self.owner = kwargs.get('owner', None) # Owner of event
            self.title = kwargs.get('title', "Title")
            self.descr = kwargs.get('descr', "Description")
            self.react = kwargs.get('react', "\U0001F1E6") # Reaction to respond to event
            self.message = None
            self.mentions = ""
            self.timestamp = datetime.datetime.now()

        async def send(self):
            msg = discord.Embed(
                title=self.title,
                description=self.descr,
                color=0xe025f5,
                timestamp=self.timestamp
            )
            msg.set_author(name=self.owner.display_name, icon_url=self.owner.avatar_url)
            msg.set_footer(text=f"Last update: {datetime.datetime.now()} mvh ikubot")

            if self.message:
                reacts = []
                for react in (await self.channel.fetch_message(self.message.id)).reactions:
                    if react.emoji == self.react:
                        reacts = await react.users().flatten()

                signups = list(filter(lambda user: not user.bot, reacts))

                i = 0
                val = ""
                for user in signups:
                    val += user.display_name
                    i += 1
                    if i == 3:
                        val += '\n'
                        i = 0
                    else:
                        val += '\t'
                if val == "":
                    val = '-'
                msg.add_field(name=f"Sign-ups: {len(signups)}", value=f"```{val}```", inline=False)
                await self.message.edit(content=self.mentions, embed=msg)
            else:
                self.message = await self.channel.send(content=self.mentions, embed=msg)
                await self.message.add_reaction(self.react)