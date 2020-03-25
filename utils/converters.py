import discord

from discord.ext import commands

# from DleanJeans/Jenna
class NitroEmojiConverter(commands.PartialEmojiConverter):
    async def convert(self, ctx, emoji_str):
        no_colon = emoji_str.replace(':', '')
        emoji = discord.utils.get(ctx.bot.emojis, name=no_colon)
        if (not emoji):
            try: 
                emoji = await super().convert(ctx, emoji_str)
            except: 
                emoji = emoji_str
        return emoji

emoji_converter = NitroEmojiConverter()
async def emoji_convert(ctx, arg):
    return await emoji_converter.convert(ctx, arg)

