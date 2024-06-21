from typing import Optional
import discord
from discord.ext import commands
from discord import app_commands
from discord import Embed
from discord.app_commands import Choice

import asyncio

from transformers import MBartForConditionalGeneration, MBart50Tokenizer
import opencc

class pickachuAI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tokenizer = MBart50Tokenizer.from_pretrained('facebook/mbart-large-50-many-to-many-mmt')
        self.translate_model = MBartForConditionalGeneration.from_pretrained('facebook/mbart-large-50-many-to-many-mmt')
    
    async def translate_feedback(self, interaction: discord.Interaction, lang2lang: Choice[str], content: str):
        embed = Embed(title=lang2lang.name, description="翻譯結果如下", color=discord.Color.from_str('#FFDC35'))
        mode_num = int(lang2lang.value)
        slang2tlang_lst = [['en_XX', 'zh_CN'], ['zh_CN', 'en_XX'], ['en_XX', 'zh_CN']]
        tgt_texts = [content]
        if mode_num < 3:
            self.tokenizer.src_lang = slang2tlang_lst[mode_num][0]
            self.tokenizer.tgt_lang = slang2tlang_lst[mode_num][1]
            inputs = self.tokenizer(content, return_tensors="pt", padding=True)
            translated_tokens = self.translate_model.generate(**inputs, forced_bos_token_id=self.tokenizer.lang_code_to_id[slang2tlang_lst[mode_num][1]])
            tgt_texts = [self.tokenizer.decode(t, skip_special_tokens=True) for t in translated_tokens]

        for i in range(0, len(tgt_texts)):
            if mode_num == 1 or mode_num == 2:
                emb_name = str(i)
                emb_value = tgt_texts[i]
                embed.add_field(name=emb_name, value=emb_value, inline=False)
            else:        
                if mode_num == 0 or mode_num == 3:
                    converter = opencc.OpenCC('s2twp.json')
                elif mode_num == 4:
                    converter = opencc.OpenCC('tw2sp.json')

                emb_value = converter.convert(tgt_texts[i])
                embed.add_field(name=content, value=emb_value, inline=False)

        await interaction.followup.send(embed=embed)

    @app_commands.command(name = '翻譯', description = '皮卡丘學會了人類的語言，但目前只會中文跟英文＠_＠')
    @app_commands.describe(lang2lang = '語言', content = '內容')
    @app_commands.choices(
        lang2lang = [
            Choice(name = '英文轉繁體中文', value = '0'),
            Choice(name = '中文轉英文', value = '1'),
            Choice(name = '英文轉簡體中文', value = '2'),
            Choice(name = '簡體中文轉繁體中文', value = '3'),
            Choice(name = '繁體中文轉簡體中文', value = '4')
        ]
    )
    async def translate(self, interaction: discord.Interaction, lang2lang: Choice[str], content: str):
        await interaction.response.send_message('piii??  pikapikachu_pika...(皮卡丘翻譯中...)')
        asyncio.create_task(self.translate_feedback(interaction, lang2lang, content))



async def setup(bot):
    await bot.add_cog(pickachuAI(bot))