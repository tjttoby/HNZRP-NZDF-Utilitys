import discord 
from discord.ext import commands, tasks 
import os 
import asyncio 
from itertools import cycle 
from dotenv import load_dotenv



bot = commands.Bot (command_prefix='!', intents=discord.Intents.all()) # Cmd (non slash) prefix. 

## ------------- BOT STATUS CYCLE ------------- #

bot_statuses = cycle(['NZDF Bot' , 'Developed by Tobytiwi', 'Created for NZDF']) # Statuses to cycle through

@tasks.loop(seconds=5) # Change status every 10 seconds 
async def change_status():
    await bot.change_presence (activity=discord.Game(next(bot_statuses))) 

 ## ------------- BOT ONLINE IN TERMANAL ------------- #
@bot.event 
async def on_ready():
    print(f'☑️ Bot online') # Print to console when bot is online
    change_status.start() # Start status change loop for statuses. 
    try:
        synced = await bot.tree.sync() 
        print(f'☑️ Synced {len(synced)} commands.') 
    except Exception as e:
        print(f"❌ ERROR: Failed to sync commands: ", e) 



# --------- GET TOKEN FROM FILE --------- #

load_dotenv(".env")
TOKEN: str = os.getenv("TOKEN") # type: ignore


# ---------------------- ERROR HANDLING ------------------ #

@bot.event
async def on_command_error(ctx, error):
    # Prefix command errors
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found. Please check the command name and try again.")
        return
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have the required permissions to use this command.")
        return
    if isinstance(error, commands.MissingRole):
        await ctx.send("❌ You don't have the required role to use this command.")
        return

    print(f"[PrefixCmdError] {getattr(ctx.command, 'qualified_name', 'unknown')}: {error}")
    
    # Try to log the error to the logging channel
    logging_cog = bot.get_cog('LoggingSystem')
    if logging_cog and hasattr(logging_cog, 'get_log_channel'):
        try:
            channel = await logging_cog.get_log_channel()  # type: ignore
            if channel:
                embed = discord.Embed(
                    title="⚠️ Prefix Command Error",
                    color=discord.Color.orange(),
                    timestamp=discord.utils.utcnow()
                )
                embed.add_field(name="Command", value=f"`{getattr(ctx.command, 'qualified_name', 'unknown')}`", inline=True)
                embed.add_field(name="User", value=f"{ctx.author.mention} ({ctx.author.display_name})", inline=True)
                embed.add_field(name="Error", value=f"```{str(error)[:500]}```", inline=False)
                await channel.send(embed=embed)
        except Exception as log_error:
            print(f"[LOGGING] Failed to log prefix command error: {log_error}")
    
    try:
        await ctx.send(f"❌ An error occurred: {error}")
    except Exception:
        pass

# Slash command (app command) errors
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    try:
        cmd_name = getattr(getattr(interaction, 'command', None), 'qualified_name', 'unknown')
        print(f"[AppCmdError] {cmd_name}: {error}")
        
        # Try to get the logging system cog for enhanced error logging
        logging_cog = bot.get_cog('LoggingSystem')
        if logging_cog and hasattr(logging_cog, 'log_error_with_ping'):
            await logging_cog.log_error_with_ping(interaction, cmd_name, error)  # type: ignore
        
        # If we haven't responded yet, send an ephemeral message; otherwise use followup
        if not interaction.response.is_done():
            await interaction.response.send_message("❌ Something went wrong running that command. The error has been logged and admins have been notified.", ephemeral=True)
        else:
            await interaction.followup.send("❌ Something went wrong running that command. The error has been logged and admins have been notified.", ephemeral=True)
    except Exception as e:
        # Last-ditch logging if even error handling fails
        print(f"[AppCmdErrorHandlerFailure] {e}")

# ---------------------- COGS ------------------ #

async def load():
    for filename in os.listdir('./Cogs'):
        if not filename.endswith('.py') or filename == '__init__.py':
            continue
        try:
            await bot.load_extension(f'Cogs.{filename[:-3]}')
            print(f"✅ Successfully loaded extension: {filename}")
        except Exception as e:
            print(f"❌ Failed to load extension {filename}: {str(e)}")

#--------------------- RUN BOT ------------------ #
async def main():
    async with bot:
        await load()
        await bot.start(TOKEN) 

asyncio.run(main())


