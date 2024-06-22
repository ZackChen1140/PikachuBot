import discord
from discord.ext import commands, tasks
from discord import Embed
import requests
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup

import torch
import torch.nn as nn
from torchvision import transforms
import torchvision.models as models

from PIL import Image
import pandas as pd

url_prefix = 'https://tw.portal-pokemon.com/play/pokedex/'

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.4850, 0.4560, 0.4060], std=[0.2290, 0.2240, 0.2250])
])

class PokeClassifier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.model = models.vit_b_32(weights=models.ViT_B_32_Weights)
        self.model.heads[0] = nn.Linear(self.model.heads[0].in_features, 28)
        self.model.load_state_dict(torch.load('cogs/datas/best_model_bit_b_32.pth', map_location=device))
        self.model.to(device)
        self.model.eval()
        self.df = pd.read_csv('cogs/datas/pokedex.csv', header=None)
        
    @commands.Cog.listener()
    async def on_message(self, message):
        # 回覆Hello, world!
        if message.author == self.bot.user:
            return
        
        if message.content.startswith('皮卡丘') and ('什麼' in message.content or '哪隻' in message.content or '哪一隻' in message.content) and ('寶可夢' in message.content or '神奇寶貝' in message.content) and message.attachments:
            image = download_image(message.attachments[0].url)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image = transform(image).unsqueeze(0)
            image = image.to(device)
            with torch.no_grad():
                outputs = self.model(image)
                _, predicted = torch.max(outputs, 1)
            poke_id =  predicted.item()
            
            response = requests.get(f'{url_prefix}{self.df.iloc[poke_id, 0]}')
            soup = BeautifulSoup(response.content, 'html.parser')
            og_img = soup.find('meta', property='og:image')
            embed = Embed(title=self.df.iloc[poke_id, 1], description=self.df.iloc[poke_id, 4], url=f'{url_prefix}{self.df.iloc[poke_id, 0]}', color=discord.Color.from_str('#FF4400'))
            embed.add_field(name='屬性', value=self.df.iloc[poke_id, 3], inline=True)
            embed.add_field(name='分類', value=f'{self.df.iloc[poke_id, 2]}寶可夢', inline=True)
            embed.set_image(url=og_img['content'])
            await message.channel.send(embed=embed)

def download_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # 確保請求成功
        image = Image.open(BytesIO(response.content))
        return image
    except Exception as e:
        print(f'Error downloading image: {e}')
        return None

async def setup(bot):
    await bot.add_cog(PokeClassifier(bot))