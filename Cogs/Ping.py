import discord 
from discord import app_commands
from discord.ext import commands 

class Ping(commands.Cog): 
    def __init__(self, bot): 
        self.bot = bot

    @commands.Cog.listener() 
    async def on_ready(self):
        print(f'⚙️ {__name__} Cog is online')
        
    @commands.command() 
    async def ping(self, ctx): 
        ping_embed = discord.Embed(title="Pong!", color=discord.Color.orange()) 
        ping_embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=False)
        ping_embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=ping_embed) 

    @app_commands.command(name="ping", description="Check the bot's latency")
    async def Sping(self, interaction: discord.Interaction): 
        ping_embed = discord.Embed(title="Pong!", color=discord.Color.orange()) 
        ping_embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=False)
        ping_embed.set_footer(text=f"Requested by {interaction.user}")
        await interaction.response.send_message(embed=ping_embed) 
    




async def setup(bot): 
    await bot.add_cog(Ping(bot)) 