import discord  
from discord.ext import commands  
import os  
import easy_pil  
import random  



class memberjoin(commands.Cog):  
    def __init__(self, bot):  
        self.bot = bot

    @commands.Cog.listener()  
    async def on_ready(self):
        print(f'⚙️ {__name__} Cog is online')
    
    @commands.Cog.listener()  
    async def on_member_join(self, member: discord.Member):  
        print(f"Member join event triggered for {member.name}")
    
        welcome_channel = member.guild.system_channel   
        if welcome_channel is None:
            print(f"ERROR: No system channel set in the server! Please set a system channel in Server Settings > Overview")
            return

        images = [image for image in os.listdir("Cogs/welcome_images/") if image.endswith ((".png", ".jpg", ".jpeg"))]  
        bg = easy_pil.Editor (f'./Cogs/welcome_images/{random.choice(images)}')
    

        image_file = discord.File (fp=bg.image_bytes, filename='welcome.png')  
        
        print(f"Trying to send welcome message to {welcome_channel.name}")
        await welcome_channel.send(f'Hello there {member.name} head to https://discord.com/channels/1427868958844784763/1427869676830195764 to apply for the NZDF!')  
        print(f"Trying to send welcome image")
        await welcome_channel.send(file=image_file)  


async def setup(bot):  
    await bot.add_cog(memberjoin(bot))  