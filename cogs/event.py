import discord
from discord.ext import commands, tasks
import asyncio
import random
from discord import Embed

import google.generativeai as genai
import opencc
import re

skills = ['十萬伏特', '電球', '電網', '鐵尾', '雷電拳', '影子分身', '伏特攻擊', '電光一閃']
skill_voice = [
    'piiika chuuuuuuuu :zap::zap::zap::zap::zap::zap::zap:', 
    'pikapikapika chupi! :zap::baseball:',
    'pikapikapika chupika! :zap::spider_web:',
    'chuuu pika! :zap::spider_web:',
    'pika! pikachuuuuu pika!chu :punch:',
    'pikah (pika!(pika!(pika!(pika!)))) :ninja::ninja::ninja:', 
    'pika! pi--ka--pi-ka-pikapika~ piiikaaaaaaa!!!! :zap::dash:',
    'pi pi pi pi :rat::dash::rat::dash::rat::dash::rat::dash:'
]

def remove_duplicates(text):
    return re.sub(r'([\u4e00-\u9fff])\1', r'\1', text)

class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open('genaikey.txt', 'r') as f:
            self.genaikey = f.read()
        genai.configure(api_key=self.genaikey)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        # self.t2s_converter = opencc.OpenCC('t2s.json')
        # self.s2twp_converter = opencc.OpenCC('s2twp.json')

    # @commands.Cog.listener()
    # async def on_ready(self):
    #     print(f"目前登入身份 --> {self.bot.user}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # 确保机器人在语音频道内
        if self.bot.voice_clients:
            voice_channel = self.bot.voice_clients[0].channel
            # 检查语音频道内是否还有其他用户
            if len(voice_channel.members) == 1:
                await asyncio.sleep(60)
                if len(voice_channel.members) == 1:
                    await voice_channel.send('piikachuu~ (皮卡丘跑走了...)')
                    await self.bot.voice_clients[0].disconnect()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        
        is_command = False
        if message.content.startswith('皮卡丘'):
            #sentence_list = message.content.split(" ",2)
            if len(message.content.strip())==3:
                is_command = True
                rm = random.randint(0, 2)
                ans = ['pi?', 'pika?', 'pikapika :smiley:']
                await message.channel.send(ans[rm])
            else:
                sentence_list = message.content.split(' ')
                if '進來' in message.content:
                    is_command = True
                    voice_channel = message.author.voice.channel
                    if voice_channel:
                        # 連接到語音頻道
                        await voice_channel.connect()
                    else:
                        await message.channel.send('pika?')
                if '離開' in message.content:
                    is_command = True
                    if self.bot.voice_clients:
                        # 離開語音頻道
                        await self.bot.voice_clients[0].disconnect()
                    else:
                        await message.channel.send('pi?')
                
                chs = ''
                for ch in message.content:
                    chs+=ch
                    for idx in range(0, len(skills)):
                        if skills[idx] in chs:
                            is_command = True
                            await message.channel.send(skill_voice[idx])
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
                    response = self.model.generate_content(content)
                    await message.channel.send(response.text)
            

    @commands.Cog.listener()
    async def on_member_join(member: discord.Member):
        for channel in member.guild.channels:
        # 如果找到了一個類型為 TextChannel 的頻道
            if isinstance(channel, discord.TextChannel):
                await channel.send('pikapika!  pikachu!\n(皮卡丘非常歡迎\"' + member.display_name + '\"的加入')

async def setup(bot):
    await bot.add_cog(Event(bot))