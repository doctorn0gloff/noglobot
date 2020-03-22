import discord

from discord.ext import commands
from utils.cogclasses import SavesDataCSV

class NhoanCount(commands.Cog, SavesDataCSV):
    def __init__(self, bot):
        self.bot = bot
        SavesDataCSV.__init__(self, "nhoan.csv", ["nhoan"], [0], lambda user: user.id)

    @commands.command(pass_context = True, aliases = ["nhoặn"])
    async def nhoan(self, ctx, member: discord.Member):
        nhoantimes = self.get_attribute_for(member, "nhoan")
        if (nhoantimes == 0):
            await ctx.send("j oi khomg {0} just posted nhoặn for the first time!".format(member.name))
        else:
            await ctx.send("j oi khomg {0} just posted nhoặn, that's {1} times now".format(member.name, str(nhoantimes + 1)))
        self.write_attribute_for(member, "nhoan", nhoantimes + 1)

    @commands.command(pass_context = True)
    async def hownhoan(self, ctx, member: discord.Member):
        nhoantimes = self.get_attribute_for(member, "nhoan")
        if (nhoantimes == 0):
            await ctx.send("{0} has never posted nhoặn. Yet!".format(member.name))
        else:
            await ctx.send("{0} has posted nhoặn {1} time{2}!".format(member.name, str(nhoantimes), "s" if nhoantimes != 1 else ""))
    
    @commands.command(pass_context = True)
    async def nhoankings(self, ctx):
        allnhoan = self.get_data_dict()
        top5 = sorted(list(allnhoan), key = lambda m_id: allnhoan[m_id]["nhoan"], reverse = True)[:5]
        await ctx.send("***Khúm núm before your nhoặn kings!***")
        for i, member_id in enumerate(top5):
            memb = self.bot.get_user(int(member_id))
            nhoantimes = allnhoan[member_id]["nhoan"]
            await ctx.send(
                "**{0}**: {1}, with {2} nhoặn post{3}".format(i+1, memb.name, nhoantimes, "s" if nhoantimes != 1 else "")
            )

def setup(bot):
    bot.add_cog(NhoanCount(bot))