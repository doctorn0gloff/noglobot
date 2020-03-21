import discord
import os
from discord.ext import commands

#initiate the bot
bot = commands.Bot(command_prefix="dm ", help_command=commands.DefaultHelpCommand(width=200))
#might write a custom HelpCommand child class later and import it in. Override the classmethods of the HelpCommand class to do so

@bot.event
async def on_ready():
    print("Logged on as:")
    print(bot.user.name)
    print(bot.user.id)
    await bot.change_presence(activity = discord.Game('dm help'))
    
cogs = [
    'base',
    'masoigame'
]

if (__name__ == "__main__"):
    for cog in cogs:
        bot.load_extension("cogs." + cog) 

bot.run(os.environ.get("DISCORD_BOT_TOKEN"))
#invite link: https://discordapp.com/oauth2/authorize?client_id=339710452319649793&scope=bot&permissions=1074265152