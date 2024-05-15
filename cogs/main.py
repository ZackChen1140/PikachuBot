import discord
from discord.ext import commands, tasks
import asyncio

change_status_period = 30 * 60

class Main(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.change_status_loop = tasks.loop(seconds=change_status_period)(self.change_status)
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"目前登入身份 --> {self.bot.user}")
        await self.bot.tree.sync()
        self.change_status_loop.start()

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(self.bot.latency)

    @commands.command()
    async def purge(self, ctx, num=1):
        deleted = await ctx.channel.purge(limit=num+1)
        await ctx.send(f'{len(deleted)} messages deleted!')

    async def change_status(self):
        statuses = [
            discord.Activity(type=discord.ActivityType.playing, name="Pokémon Scarlet & Violet"),
            discord.Activity(type=discord.ActivityType.watching, name="Pokémon Horizons")
        ]
        for status in statuses:
            await self.bot.change_presence(activity=status)
            await asyncio.sleep(change_status_period)


async def setup(bot):
    await bot.add_cog(Main(bot))