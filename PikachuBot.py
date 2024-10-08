# 導入Discord.py模組
import discord
# 導入commands指令模組
from discord.ext import commands, tasks
from discord import app_commands
import os
import asyncio
import random

with open('bottoken.txt', 'r') as f:
    token = f.read()

# intents是要求機器人的權限
intents = discord.Intents.all()
intents.message_content = True
# command_prefix是前綴符號，可以自由選擇($, #, &...)

client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix = '', intents = intents)

# 載入指令程式檔案
@bot.command()
async def load(ctx, extension):
    await bot.load_extension(f"cogs.{extension}")
    await ctx.send(f"Loaded {extension} done.")

# 卸載指令檔案
@bot.command()
async def unload(ctx, extension):
    await bot.unload_extension(f"cogs.{extension}")
    await ctx.send(f"UnLoaded {extension} done.")

# 重新載入程式檔案
@bot.command()
async def reload(ctx, extension):
    await bot.reload_extension(f"cogs.{extension}")
    await ctx.send(f"ReLoaded {extension} done.")


async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")


async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    await load_extensions()
    await bot.start(token)

asyncio.run(main())