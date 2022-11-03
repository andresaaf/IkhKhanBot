from IFeature import IFeature
import discord

class MapleStory(IFeature):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_message(self, message):
        msg = message.content.split(' ')
        if msg[0] == '.maple':
            if msg[1] == 'sf':
                ilvl = msg[2] if len(msg) == 3 else '140'
                await self.post_star_force_embed(ilvl)

    SF_ITEMS = {
        '200': [
            'https://static.wikia.nocookie.net/maplestory/images/8/83/Eqp_Endless_Terror.png',
        ],

        '160': [
            'https://static.wikia.nocookie.net/maplestory/images/b/bb/Eqp_Source_of_Suffering.png'
        ],

        '150': [
            'https://static.wikia.nocookie.net/maplestory/images/6/61/Eqp_Superior_Gollux_Ring.png'
        ],

        '140': [
            'https://static.wikia.nocookie.net/maplestory/images/c/c3/Eqp_Dominator_Pendant.png'
        ]
    }
    async def post_star_force_embed(self):
        pass