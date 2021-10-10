from discord.ext import commands
from keep_alive import keep_alive
from dotenv import load_dotenv
import os

bot = commands.Bot(command_prefix="!")


# Loads our cogs library
@bot.command()
@commands.has_permissions(administrator=True)
async def load(ctx, extension):
    bot.load_extension(f"cogs.{extension}")


# Unloads our cogs library
@bot.command()
@commands.has_permissions(administrator=True)
async def unload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")


for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

load_dotenv()
keep_alive()
bot.run(os.getenv('TOKEN'))
