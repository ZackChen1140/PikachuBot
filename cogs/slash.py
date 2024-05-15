from typing import Optional
import discord
from discord.ext import commands
from discord import app_commands
from discord import Embed
from discord.app_commands import Choice

import random
import asyncio
import datetime

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cred = credentials.Certificate('pikachubot-db-4a94b-firebase-adminsdk-sm9rn-096b5c4f33.json')
        self.app = firebase_admin.initialize_app(self.cred)
        self.db = firestore.client()
    
    async def send_after_delay(self, interaction: discord.Interaction, delay: int, msg: str):
        await asyncio.sleep(delay)
        await interaction.followup.send(msg)
    
    @app_commands.command(name = '計時', description = '讓皮卡丘幫你計時吧~(最多60分鐘)')
    @app_commands.describe(minute = '輸入整數', second = '輸入整數')
    async def Count(self, interaction: discord.Interaction, minute: int, second: int):
        if minute > 60 or (minute == 60 and second >= 1) or (minute + (second / 60) > 60):
            await interaction.response.send_message('pikapika??(皮卡丘無法計時超過60分鐘)')
        elif minute < 0 or second < 0 or (minute == 0 and second == 0):
            await interaction.response.send_message('pikapika??')
        else:
            s = minute * 60 + second
            await interaction.response.send_message('pi..ka..pi..ka..pi..ka....(皮卡丘計時中)')
            asyncio.create_task(self.send_after_delay(interaction, s, 'pika! pika!! piiika chuuuuuuu!!!!!!!'))
    
    @app_commands.command(name = '分組', description = '皮卡丘幫你分組')
    @app_commands.describe(group_title = '分組主題', groups_number = '組別數量', members = '成員列表(請用,分隔)')
    async def Group(self, interaction: discord.Interaction, group_title: str, groups_number: int, members: str):
        embed = Embed(title=group_title, description="分組結果如下", color=discord.Color.from_str('#FFDC35'))
        member_lst = members.split(',')
        if groups_number <= 0 or len(members.strip()) == 0 or len(member_lst)==1 or groups_number >= len(member_lst):
            await interaction.response.send_message('pikapika??')
        else:
            random.shuffle(member_lst)
            groups_lst = list()
            for i in range(0, groups_number):
                groups_lst.append(list())
            
            group_idx = 0
            for member in member_lst:
                groups_lst[group_idx].append(member)
                group_idx += 1
                group_idx %= groups_number

            for i in range(0, groups_number):
                emb_name = '第' + str(i + 1) + '組: '
                emb_value = ','.join(groups_lst[i])
                embed.add_field(name=emb_name, value=emb_value, inline=False)

            await interaction.response.send_message(embed=embed)

    @app_commands.command(name = '吃什麼', description = '皮卡丘喜歡吃番茄醬~')
    @app_commands.describe(meal_time = '用餐時段')
    @app_commands.choices(
        meal_time = [
            Choice(name = '早餐', value = 'breakfast'),
            Choice(name = '早午餐', value = 'brunch'),
            Choice(name = '午餐', value = 'lunch'),
            Choice(name = '下午茶', value = 'afternoon tea'),
            Choice(name = '晚餐', value = 'dinner'),
            Choice(name = '宵夜', value = 'late night snack')
        ]
    )
    async def Meals(self, interaction: discord.Interaction, meal_time: Choice[str]):
        server_id = str(interaction.guild.id)
        doc_ref = self.db.collection(server_id).document('meals')
        doc = doc_ref.get()
        if doc.exists:
            meals_dic = doc.to_dict()
            if meal_time.value in meals_dic.keys():
                meal_list = meals_dic[meal_time.value]
                random.shuffle(meals_dic.get(meal_time.value))
                await interaction.response.send_message('pikachu~\n' + meal_time.name + ': ' + meals_dic.get(meal_time.value)[0])
            else:
                await interaction.response.send_message('pikachu?\n(皮卡丘還不知道這個時段有什麼好吃的，快新增餐廳吧～)')
        else:
            await interaction.response.send_message('pikachu?\n(皮卡丘還不知道有什麼好吃的，快新增餐廳吧～)')

    @app_commands.command(name = '新增餐廳', description = '皮卡丘想吃別的...')
    @app_commands.describe(meal_time = '用餐時段', restaurant = '餐廳名稱')
    @app_commands.choices(
        meal_time = [
            Choice(name = '早餐', value = 'breakfast'),
            Choice(name = '早午餐', value = 'brunch'),
            Choice(name = '午餐', value = 'lunch'),
            Choice(name = '下午茶', value = 'afternoon tea'),
            Choice(name = '晚餐', value = 'dinner'),
            Choice(name = '宵夜', value = 'late night snack')
        ]
    )
    async def addRestaurant(self, interaction: discord.Interaction, meal_time: Choice[str], restaurant: str):
        server_id = str(interaction.guild.id)
        restaurant = restaurant.strip()
        doc_ref = self.db.collection(server_id).document('meals')
        doc = doc_ref.get()
        if doc.exists:
            meals_dic = doc.to_dict()
            if meal_time.value not in meals_dic.keys():
                meals_dic.update({meal_time.value : [restaurant]})
                doc_ref.set(meals_dic)
                await interaction.response.send_message('pikachu!\n(已在\"' + meal_time.name + '\"時段新增\"' + restaurant + '\"了！)')
            else:
                restaurants_lst = meals_dic[meal_time.value]
                if restaurant in restaurants_lst:
                    await interaction.response.send_message('pikachu?\n(\"' + meal_time.name + '\"時段已經有\"' + restaurant + '\"了！)')
                else:
                    restaurants_lst.append(restaurant)
                    meals_dic.update({meal_time.value : restaurants_lst})
                    doc_ref.set(meals_dic)
                    await interaction.response.send_message('pikachu!\n(已在\"' + meal_time.name + '\"時段新增\"' + restaurant + '\"了！)')
        else:
            doc_ref.set({meal_time.value : [restaurant]})
            await interaction.response.send_message('pikachu!\n(已在\"' + meal_time.name + '\"時段新增\"' + restaurant + '\"了！)')

    @app_commands.command(name = '刪除餐廳', description = '皮卡丘不喜歡吃這家')
    @app_commands.describe(meal_time = '用餐時段')
    @app_commands.choices(
        meal_time = [
            Choice(name = '早餐', value = 'breakfast'),
            Choice(name = '早午餐', value = 'brunch'),
            Choice(name = '午餐', value = 'lunch'),
            Choice(name = '下午茶', value = 'afternoon tea'),
            Choice(name = '晚餐', value = 'dinner'),
            Choice(name = '宵夜', value = 'late night snack'),
            Choice(name = '全部', value='all')
        ]
    )
    async def removeRestaurant(self, interaction: discord.Interaction, meal_time: Choice[str], restaurant: str):
        server_id = str(interaction.guild.id)
        restaurant = restaurant.strip()
        doc_ref = self.db.collection(server_id).document('meals')
        doc = doc_ref.get()
        if doc.exists:
            meals_dic = doc.to_dict()
            if (meal_time.value != 'all') and (meal_time.value not in meals_dic.keys()):
                await interaction.response.send_message('pikachu?\n(皮卡丘沒有在\"' + meal_time.name + '\"時間吃過這家餐廳喔～)')
            else:
                if meal_time.value == 'all':
                    value_lst = ['breakfast', 'brunch', 'lunch', 'afternoon tea', 'dinner', 'late night snack']

                    is_in_dict = False
                    for i in range(0, len(value_lst)):
                        if value_lst[i] in meals_dic.keys():
                            if restaurant in meals_dic[value_lst[i]]:
                                is_in_dict = True
                                meals_dic[value_lst[i]].remove(restaurant)
                    
                    if is_in_dict:
                        doc_ref.set(meals_dic)
                        await interaction.response.send_message('pikachu!\n(皮卡丘在\"' + meal_time.name + '\"時段刪除了\"' + restaurant + '\")')
                    else:
                        await interaction.response.send_message('pikachu?\n(皮卡丘沒有吃過這家餐廳喔～)')        
                else:
                    if meal_time.value in meals_dic.keys():
                        if restaurant in meals_dic[meal_time.value]:
                            meals_dic[meal_time.value].remove(restaurant)
                            doc_ref.set(meals_dic)
                            await interaction.response.send_message('pikachu!\n(皮卡丘在\"' + meal_time.name + '\"時段刪除了\"' + restaurant + '\")')
                        else:
                            await interaction.response.send_message('pikachu?\n(皮卡丘沒有在\"' + meal_time.name + '\"時間吃過這家餐廳喔～)')
                    else:
                        await interaction.response.send_message('pikachu?\n(皮卡丘沒有在\"' + meal_time.name + '\"時間吃過這家餐廳喔～)')
        else:
            if meal_time.value == 'all':
                await interaction.response.send_message('pikachu?\n(皮卡丘沒有吃過這家餐廳喔～)')
            else:
                await interaction.response.send_message('pikachu?\n(皮卡丘沒有在\"' + meal_time.name + '\"時間吃過這家餐廳喔～)')

    @app_commands.command(name = '查看餐廳', description = '讓皮卡丘想想...')
    @app_commands.describe(meal_time = '用餐時段')
    @app_commands.choices(
        meal_time = [
            Choice(name = '早餐', value = 'breakfast'),
            Choice(name = '早午餐', value = 'brunch'),
            Choice(name = '午餐', value = 'lunch'),
            Choice(name = '下午茶', value = 'afternoon tea'),
            Choice(name = '晚餐', value = 'dinner'),
            Choice(name = '宵夜', value = 'late night snack'),
            Choice(name = '全部', value='all')
        ]
    )
    async def showRestaurants(self, interaction: discord.Interaction, meal_time: Choice[str]):
        server_id = str(interaction.guild.id)
        doc_ref = self.db.collection(server_id).document('meals')
        doc = doc_ref.get()
        if doc.exists:
            meals_dic = doc.to_dict()
            if (meal_time.value != 'all') and (meal_time.value not in meals_dic.keys()):
                await interaction.response.send_message('pikachu?\n(\"' + meal_time.name + '\"時段沒有任何餐廳喔～)')
            else:
                if meal_time.value == 'all':
                    name_lst = ['早餐', '早午餐', '午餐', '下午茶', '晚餐', '宵夜']
                    value_lst = ['breakfast', 'brunch', 'lunch', 'afternoon tea', 'dinner', 'late night snack']

                    output_str = 'pika:thinking:......pikachu!:grinning:'

                    output_dic = dict()
                    for i in range(0, len(name_lst)):
                        if value_lst[i] in meals_dic.keys():
                            output_str += ('\n' + name_lst[i] + ' : ' + str(meals_dic[value_lst[i]]))
                    
                    await interaction.response.send_message(output_str)
                else:
                    output_str = 'pika:thinking:......pikachu!:grinning:'
                    output_str += ('\n' + meal_time.name + ' : ' + str(meals_dic[meal_time.value]))
                    await interaction.response.send_message(output_str)
        else:
            await interaction.response.send_message('pikachu?\n(目前還沒有任何餐廳喔～)')
            
async def setup(bot):
    await bot.add_cog(Slash(bot))
