import discord
from discord.ext import commands

from google import genai
from google.genai import types

import asyncio
import random

import cogs.datas.skills as skills



class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open('genaikey.txt', 'r') as f:
            self.genaikey = f.read()
        self.client = genai.Client(api_key=self.genaikey)
        self.config = types.GenerateContentConfig(
            temperature=0.5,
            max_output_tokens=1024,
            system_instruction="All responses must be written in Traditional Chinese as commonly used in Taiwan"
        )

    def generate_content(self, prompt):
        try:
            response = self.client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt,
                config=self.config
            )
            return response.text
        except Exception as e:
            print(f"Error generating content: {e}")
            return "Pikachu~~ zzZ(皮卡丘暫時無法回應)"

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        async with message.channel.typing():
            is_command = False
            if message.content.startswith('皮卡丘'):
                if len(message.content.strip())==3:
                    is_command = True
                    rm = random.randint(0, 2)
                    ans = ['pi?', 'pika?', 'pikapika :smiley:']
                    await message.channel.send(ans[rm])
                else:
                    chs = ''
                    for ch in message.content:
                        chs+=ch
                        for idx in range(0, len(skills.skill_names)):
                            if skills.skill_names[idx] in chs:
                                is_command = True
                                await message.channel.send(skills.skill_voice[idx])
                                chs = ''
            
            if not is_command:
                server_id = str(message.guild.id)
                doc_ref = self.bot.db.collection(server_id).document('genai')
                doc = doc_ref.get()
                if doc.exists:
                    channels = doc.to_dict().get('channels')
                    if str(message.channel.id) in channels:
                        content = message.content.strip()
                        if content.startswith('皮卡丘'):
                            content = content[3:].strip()
                        response = self.generate_content(content)
                        await message.channel.send(response)
        
            

    @commands.Cog.listener()
    async def on_member_join(member: discord.Member):
        for channel in member.guild.channels:
        # 如果找到了一個類型為 TextChannel 的頻道
            if isinstance(channel, discord.TextChannel):
                await channel.send('pikapika!  pikachu!\n(皮卡丘非常歡迎\"' + member.display_name + '\"的加入')

async def setup(bot):
    await bot.add_cog(Event(bot))