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
    async def whois(self, ctx, memberID):
        try:
            memberIDint = int(memberID)
        except:
            await ctx.send("Unable to convert argument into ID integer")
        member = self.bot.get_user(memberIDint)
        await ctx.send("Member with ID {0} is {1}".format(memberIDint, str(member)))

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
