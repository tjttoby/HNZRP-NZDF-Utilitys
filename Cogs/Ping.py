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
        ping_embed.add_field(name=f"{self.bot.user.name}'s Latency (ms)", value=f"{round(self.bot.latency * 1000)}ms", inline=False)
        # use display_avatar.url to be compatible with all users
        try:
            icon_url = ctx.author.display_avatar.url 
        except Exception:
            icon_url = None
        ping_embed.set_footer(text=f"Requested by {ctx.author}", icon_url=icon_url)
        await ctx.send(embed=ping_embed) 

    @app_commands.command(name="ping", description="Check the bot's latency")
    async def Sping(self, interaction: discord.Interaction): 
        ping_embed = discord.Embed(title="Pong!", color=discord.Color.orange()) 
        ping_embed.add_field(name=f"{self.bot.user.name}'s Latency (ms)", value=f"{round(self.bot.latency * 1000)}ms", inline=False)
        # use display_avatar.url to be compatible with all users
        try:
            icon_url = interaction.user.display_avatar.url 
        except Exception:
            icon_url = None
        ping_embed.set_footer(text=f"Requested by {interaction.user}", icon_url=icon_url)
        await interaction.response.send_message(embed=ping_embed) 
    
@commands.command(name = "ping", description="Check the bot's latency")



async def  commandName(self, ctx:commands.Context):
    await ctx.send("template command")






async def setup(bot): 
    await bot.add_cog(Ping(bot)) 