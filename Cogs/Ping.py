import discord 
from discord import app_commands
from discord.ext import commands 

class Ping(commands.Cog): 
    def __init__(self, bot): 
        self.bot = bot

    @app_commands.command(name="ping", description="Check the bot's latency")
    async def ping(self, interaction: discord.Interaction): 
        """Check bot latency with a clean, informative embed."""
        latency_ms = round(self.bot.latency * 1000)
        
        # Determine latency status and color
        if latency_ms < 100:
            status = "🟢 Excellent"
            color = discord.Color.green()
        elif latency_ms < 200:
            status = "🟡 Good"
            color = discord.Color.yellow()
        elif latency_ms < 300:
            status = "🟠 Fair"
            color = discord.Color.orange()
        else:
            status = "🔴 Poor"
            color = discord.Color.red()
        
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Bot latency information",
            color=color
        ) 
        embed.add_field(
            name="📡 Latency", 
            value=f"**{latency_ms}ms**\n{status}", 
            inline=True
        )
        embed.add_field(
            name="🤖 Status",
            value="✅ Online & Ready",
            inline=True
        )
        embed.set_footer(
            text=f"Requested by {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url
        )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot): 
    await bot.add_cog(Ping(bot)) 