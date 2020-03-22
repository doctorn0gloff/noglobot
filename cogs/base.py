import discord

from discord.ext import commands

class Base(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def bark(self, ctx):
        """make it bark"""
        await ctx.send("Woof!")
        
    @commands.command(pass_context=True)
    @commands.is_owner()
    async def goaway(self, ctx):
        await ctx.send("okay i'll leave now")
        await self.bot.logout()

    @commands.command(pass_context=True)
    @commands.is_owner()
    async def cogrl(self, ctx, cogname):
        self.bot.reload_extension("cogs."+cogname)
        await ctx.send("reloaded {}".format(cogname))

    @commands.Cog.listener()
    async def on_message(self,message):
        if message.author == self.bot.user:
            return
        # if message.content.startswith("dm "):
        #     await self.bot.process_commands(message)

def setup(bot):
    bot.add_cog(Base(bot))
