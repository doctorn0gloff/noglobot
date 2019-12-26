import asyncio
import discord
from discord.ext import commands

import msgame.classes

#initiate the bot
bot = commands.Bot(command_prefix="&", help_command=commands.DefaultHelpCommand(width=200))
#might write a custom HelpCommand child class later and import it in. Override the classmethods of the HelpCommand class to do so

#if im gonna migrate this to a cog later, i should copy over this bottaskmanager as well. Each cog will have its own bottaskmanager. Probably should rename to CogTaskManager or something, but yeah.
#when migrating to cog, everything should be wrapped in a MyCog class, and every function in the commands should be prefixed with self. @bot.command() becomes @commands.command()
class BotTaskManager():
    def __init__(self):
        self.tasks = dict()
        self.workingmsgs = dict()
    
    def start_masoi(self, gamemaster):
        newgame = msgame.classes.Game(gamemaster)
        self.tasks[gamemaster] = newgame
        
        #identify each running task or masoi game with its gamemaster, and access each game by the user currently requesting commands.
        #author user from the command message's ctx will be passed along to the bot task manager's running tasks (running objects) dict, as index names to refer to the correct Game instance.
        #this way, there is functionality to restrict access to a game or a task to the gamemaster or user that requested it (because the wrong user making a command will call an index without an associated game so nothing will happen)

bottaskmgr = BotTaskManager()
#the point of the bottaskmanager is to allow multiple instances of a game or task object to run at once, each having an owner user.

@bot.event
async def on_ready():
    print("Logged on as:")
    print(bot.user.name)
    print(bot.user.id)
    
    
#declaring the bot's commands
@bot.command(pass_context=True)
async def bark(ctx):
    """make it bark"""
    await ctx.send("Woof!")
    
@bot.command(pass_context=True)
async def goaway(ctx):
    if await bot.is_owner(ctx.author): #if the guy who invoked this command is me, then
        await ctx.send("okay i'll leave now")
        await bot.logout()

@bot.group(pass_context=True)
async def ms(ctx):
#add here when there are more modules and games: a check whether the Task registered in the author's name in the BotTaskManager is indeed of type masoi game (msgame.classes.Game).
    if ctx.invoked_subcommand is None:
        await ctx.send("invalid subcommand passed!")



#commands for the masoi game
@ms.command(pass_context=True)
async def newgame(ctx, member: discord.Member):
    """Cách dùng: &ms newgame @user. Tạo game masói mới với quản trò là @user. Tạo xong game sẽ chưa bắt đầu; dùng các lệnh setup để nhập các người chơi, các nhân vật, và phân vai đã."""
    if not isinstance(member, discord.Member):
        await ctx.send("invalid argument: expected a discord user tag. Usage: &ms start @user")
        return
    bottaskmgr.start_masoi(member)

@ms.command(pass_context=True)
async def printdebug(ctx):
    bottaskmgr.tasks[ctx.author].game_printdebug()
    
#setup commands
@ms.group(pass_context=True)
async def setup(ctx):
    """Cách dùng: &ms setup <players|characters|randomassign>. Các lệnh setup game trước khi chơi."""
    if ctx.invoked_subcommand is None:
        await ctx.send("invalid subcommand passed to the `setup` subcommand!")

@setup.command(pass_context=True)
async def players(ctx, *args):
    """Cách dùng: &ms setup players @player1 @player2 @player3... Nhập danh sách người chơi."""
    bottaskmgr.tasks[ctx.author].game_addconfig("entered_members", [await commands.MemberConverter().convert(ctx, arg) for arg in args])
    #MemberConverter() instance is used to convert incoming arg strings into discord.Member objects

@setup.command(pass_context=True)
async def characters(ctx, *args):
    """Cách dùng: &ms setup characters vlgr wolf secg vlgr ... Nhập các mã nhân vật dùng trong game (lặp lại để thể hiện số nhân vật đó trong game). Dùng &ms info characters để xem mã nv."""
    bottaskmgr.tasks[ctx.author].game_addconfig("allowed_chars",[arg for arg in args])

@setup.command(pass_context=True)
async def randomassign(ctx):
    """Cách dùng: &ms setup randomassign. Sau khi setup các người chơi và các nhân vật, dùng lệnh này để phân vai ngẫu nhiên."""
    await ctx.send(bottaskmgr.tasks[ctx.author].roster_randomassign())

    
#info commands
@ms.group(pass_context=True)
async def info(ctx):
    """Cách dùng: &ms info <players|characters>. Các lệnh xem thông tin về game."""
    if ctx.invoked_subcommand is None:
        await ctx.send("invalid subcommand passed to the `info` subcommand!")

@info.command(pass_context=True, name="players")
async def roster(ctx):
    """Cách dùng: &ms info players. Xem danh sách người chơi và DM cho quản trò danh sách người chơi + nhân vật."""
    await ctx.send(bottaskmgr.tasks[ctx.author].roster_getsummary(False))
    await bot.send_message(ctx.author, bottaskmgr.tasks[ctx.author].roster_getsummary(True))

@info.command(pass_context=True, name="characters")
async def charactercodes(ctx):
    """Cách dùng: &ms info characters. Xem danh sách các mã nhân vật."""
    await ctx.send(bottaskmgr.tasks[ctx.author].listcharactercodes())

    
#game control commands
@ms.group(pass_context=True)
async def game(ctx):
    """Cách dùng: &ms game <start|kill|revive|newday|newnight|killvote>. Các lệnh để quản trò điều khiển game."""
    if ctx.invoked_subcommand is None:
        await ctx.send("invalid subcommand passed to the `game` subcommand!")
@game.command(pass_context=True)
async def start(ctx):
    """Cách dùng: &ms game start. Setup xong chạy lệnh này để bắt đầu chơi."""
    await ctx.send(bottaskmgr.tasks[ctx.author].game_start())
@game.command(pass_context=True, name="end")
async def endgame(ctx):
    """Cách dùng: &ms game end. Lệnh kết thúc game trước khi một phe đã chết hết."""
    await ctx.send(bottaskmgr.tasks[ctx.author].game_detect_end(True))
#commands to be implemented: kill, resurrect, newday, startnight, votekillstart
@game.command(pass_context=True)
async def kill(ctx, member: discord.Member):
    """Cách dùng: &ms game kill @player. Kill người chơi @player."""
    bottaskmgr.tasks[ctx.author].game_kill(member)
@game.command(pass_context=True)
async def revive(ctx, member: discord.Member):
    """Cách dùng: &ms game revive @player. Hồi sinh người chơi đã chết."""
    bottaskmgr.tasks[ctx.author].game_rezz(member)
@game.command(pass_context=True)
async def newday(ctx):
    """Cách dùng: &ms game newday. Dùng lúc đêm để sang ngày mới."""
    await ctx.send(bottaskmgr.tasks[ctx.author].game_day_new())
@game.command(pass_context=True)
async def newnight(ctx):
    """Cách dùng: &ms game newnight. Dùng ban ngày để bắt đầu đêm"""
    await ctx.send(bottaskmgr.tasks[ctx.author].game_day_night())
@game.command(pass_context=True)
async def killvote(ctx):
    """Cách dùng: &ms game killvote. Bắt đầu vote để kill người chơi. React để vote."""
    bottaskmgr.tasks[ctx.author].vote_kill_start(-1) #a vote that just selects the highest voted, instead of going off any ratios.
    #get emotes of the server
    emojilist = list(bot.emojis)
    msgtext, howmanyemojis = bottaskmgr.tasks[ctx.author].vote_make_message(emojlist)
    pollmsg = await ctx.send(msgtext)
    #then bot adds reactions to the poll message it created
    for i in range(howmanyemojis):
        await pollmsg.add_reaction(emojilist[i])
        
    bottaskmgr.workingmsgs[ctx.author] = pollmsg #puts the Message object just created into the workingmsgs dict of the taskmanager, with the same gamemaster as index.
    
    
@ms.error
async def ms_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        await ctx.send("Bạn không phải là quản trò cho game ma sói nào cả!")
    
#to migrate events to a cog, replace the @bot.event decorators with @commands.Cog.listener() and instances of bot become self.bot
@bot.event
async def on_reaction_add(reaction, user):
    if not user == bot.user: #if someone other than the bot...
        if reaction.message in bottaskmgr.workingmsgs.values():
            for taskowner, msg in bottaskmgr.workingmsgs.iteritems():
                if msg == reaction.message:#...reacted to the correct poll message
                    votestatus = bottaskmgr.tasks[taskowner].vote_kill_add(bottaskmgr.tasks[taskowner].emoji_to_candidate_dict[reaction.emoji])
                    #later, should generalize to all workingmsgs for all tasks other than a masoi game by checking the type of bottaskmgr.tasks[taskowner]
                    if not votestatus == "":
                        msg.channel.send(content=votestatus)
@bot.event
async def on_message(message):
	if message.author == bot.user:
		return
	if message.content.startswith("&"):
		await bot.process_commands(message)

        
#run the damn thing
bot.run("")
#invite link: https://discordapp.com/oauth2/authorize?client_id=339710452319649793&scope=bot&permissions=1074265152