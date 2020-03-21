import discord

from discord.ext import commands
from utils.taskmgr import CogTaskManager
from functionality.masoi import Masoi

class MasoiGame(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.taskmgr = CogTaskManager()

    @commands.group(pass_context=True)
    async def ms(self, ctx):
    #add here when there are more modules and games: a check whether the Task registered in the author's name in the BotTaskManager is indeed of type masoi game (msgame.classes.Game).
        if ctx.invoked_subcommand is None:
            await ctx.send("invalid subcommand passed!")

    #commands for the masoi game
    @ms.command(pass_context=True)
    async def newgame(self, ctx, member: discord.Member):
        """Cách dùng: &ms newgame @user. Tạo game masói mới với quản trò là @user. Tạo xong game sẽ chưa bắt đầu; dùng các lệnh setup để nhập các người chơi, các nhân vật, và phân vai đã."""
        if not isinstance(member, discord.Member):
            await ctx.send("invalid argument: expected a discord user tag. Usage: &ms start @user")
            return
        self.taskmgr.start_task(member, Masoi)

    @ms.command(pass_context=True)
    async def printdebug(self, ctx):
        self.taskmgr.get_task(ctx.author).game_printdebug()
        
    #setup commands
    @ms.group(pass_context=True)
    async def setup(self, ctx):
        """Cách dùng: &ms setup <players|characters|randomassign>. Các lệnh setup game trước khi chơi."""
        if ctx.invoked_subcommand is None:
            await ctx.send("invalid subcommand passed to the `setup` subcommand!")

    @setup.command(pass_context=True)
    async def players(self, ctx, *args):
        """Cách dùng: &ms setup players @player1 @player2 @player3... Nhập danh sách người chơi."""
        self.taskmgr.get_task(ctx.author).game_addconfig("entered_members", [await commands.MemberConverter().convert(ctx, arg) for arg in args])
        #MemberConverter() instance is used to convert incoming arg strings into discord.Member objects

    @setup.command(pass_context=True)
    async def characters(self, ctx, *args):
        """Cách dùng: &ms setup characters vlgr wolf secg vlgr ... Nhập các mã nhân vật dùng trong game (lặp lại để thể hiện số nhân vật đó trong game). Dùng &ms info characters để xem mã nv."""
        self.taskmgr.get_task(ctx.author).game_addconfig("allowed_chars",[arg for arg in args])

    @setup.command(pass_context=True)
    async def randomassign(self, ctx):
        """Cách dùng: &ms setup randomassign. Sau khi setup các người chơi và các nhân vật, dùng lệnh này để phân vai ngẫu nhiên."""
        await ctx.send(self.taskmgr.get_task(ctx.author).roster_randomassign())

        
    #info commands
    @ms.group(pass_context=True)
    async def info(self, ctx):
        """Cách dùng: &ms info <players|characters>. Các lệnh xem thông tin về game."""
        if ctx.invoked_subcommand is None:
            await ctx.send("invalid subcommand passed to the `info` subcommand!")

    @info.command(pass_context=True, name="players")
    async def roster(self, ctx):
        """Cách dùng: &ms info players. Xem danh sách người chơi và DM cho quản trò danh sách người chơi + nhân vật."""
        await ctx.send(self.taskmgr.get_task(ctx.author).roster_getsummary(False))
        await self.bot.send_message(ctx.author, self.taskmgr.get_task(ctx.author).roster_getsummary(True))

    @info.command(pass_context=True, name="characters")
    async def charactercodes(self, ctx):
        """Cách dùng: &ms info characters. Xem danh sách các mã nhân vật."""
        await ctx.send(self.taskmgr.get_task(ctx.author).listcharactercodes())

        
    #game control commands
    @ms.group(pass_context=True)
    async def game(self, ctx):
        """Cách dùng: &ms game <start|kill|revive|newday|newnight|killvote>. Các lệnh để quản trò điều khiển game."""
        if ctx.invoked_subcommand is None:
            await ctx.send("invalid subcommand passed to the `game` subcommand!")
    @game.command(pass_context=True)
    async def start(self, ctx):
        """Cách dùng: &ms game start. Setup xong chạy lệnh này để bắt đầu chơi."""
        await ctx.send(self.taskmgr.get_task(ctx.author).game_start())
    @game.command(pass_context=True, name="end")
    async def endgame(self, ctx):
        """Cách dùng: &ms game end. Lệnh kết thúc game trước khi một phe đã chết hết."""
        await ctx.send(self.taskmgr.get_task(ctx.author).game_detect_end(True))
    #commands to be implemented: kill, resurrect, newday, startnight, votekillstart
    @game.command(pass_context=True)
    async def kill(self, ctx, member: discord.Member):
        """Cách dùng: &ms game kill @player. Kill người chơi @player."""
        self.taskmgr.get_task(ctx.author).game_kill(member)
    @game.command(pass_context=True)
    async def revive(self, ctx, member: discord.Member):
        """Cách dùng: &ms game revive @player. Hồi sinh người chơi đã chết."""
        self.taskmgr.get_task(ctx.author).game_rezz(member)
    @game.command(pass_context=True)
    async def newday(self, ctx):
        """Cách dùng: &ms game newday. Dùng lúc đêm để sang ngày mới."""
        await ctx.send(self.taskmgr.get_task(ctx.author).game_day_new())
    @game.command(pass_context=True)
    async def newnight(self, ctx):
        """Cách dùng: &ms game newnight. Dùng ban ngày để bắt đầu đêm"""
        await ctx.send(self.taskmgr.get_task(ctx.author).game_day_night())
    # @game.command(pass_context=True)
    # async def killvote(self, ctx):
    #     """Cách dùng: &ms game killvote. Bắt đầu vote để kill người chơi. React để vote."""
    #     self.taskmgr.get_task(ctx.author).vote_kill_start(-1) #a vote that just selects the highest voted, instead of going off any ratios.
    #     #get emotes of the server
    #     emojilist = list(self.bot.emojis)
    #     msgtext, howmanyemojis = self.taskmgr.get_task(ctx.author).vote_make_message(emojlist)
    #     pollmsg = await ctx.send(msgtext)
    #     #then bot adds reactions to the poll message it created
    #     for i in range(howmanyemojis):
    #         await pollmsg.add_reaction(emojilist[i])
            
    #     self.taskmgr.workingmsgs[ctx.author] = pollmsg 
    #     #puts the Message object just created into the workingmsgs dict of the taskmanager, with the same gamemaster as index.
        
        
    @ms.error
    async def ms_error(self, ctx, error):
        print(str(error))
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send("Bạn không phải là quản trò cho game ma sói nào cả!")
        
    #to migrate events to a cog, replace the @bot.event decorators with @commands.Cog.listener() and instances of bot become self.bot
    #@commands.Cog.listener()
    # async def on_reaction_add(self, reaction, user):
    #     if not user == self.bot.user: #if someone other than the bot...
    #         if reaction.message in self.taskmgr.workingmsgs.values():
    #             for taskowner, msg in self.taskmgr.workingmsgs.iteritems():
    #                 if msg == reaction.message:#...reacted to the correct poll message
    #                     votestatus = self.taskmgr.tasks[taskowner].vote_kill_add(self.taskmgr.tasks[taskowner].emoji_to_candidate_dict[reaction.emoji])
    #                     #later, should generalize to all workingmsgs for all tasks other than a masoi game by checking the type of self.taskmgr.tasks[taskowner]
    #                     if not votestatus == "":
    #                         msg.channel.send(content=votestatus)

def setup(bot):
    bot.add_cog(MasoiGame(bot))