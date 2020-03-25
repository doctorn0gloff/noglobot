import discord

from discord.ext import commands
from utils.cogclasses import Reactable

class ReactTest(commands.Cog, Reactable):
    def __init__(self, bot):
        self.bot = bot
        Reactable.__init__(self)

    @commands.command(pass_context = True, hidden = True)
    @commands.is_owner()
    async def reacttest(self, ctx):
        msg = await ctx.send("react with yes or no")
        await self.make_message_reactable(ctx, msg, ctx.author, ['⭕','❌'], [1,0])
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        await self.on_react(
            self.bot, reaction, user, 
            lambda c, u: "{0} chose {1}".format(u.name, "yes" if c == 1 else "no")
            )

def setup(bot):
    bot.add_cog(ReactTest(bot))

