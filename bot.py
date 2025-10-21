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


# ---------------------- COGS ------------------ #

async def load():
    for filename in os.listdir('./Cogs'):
        # skip the package __init__ and only load actual cog modules
        if filename.endswith('.py') and filename != '__init__.py':
            await bot.load_extension(f'Cogs.{filename[:-3]}') # removes .py from filename.
            print(f"Loaded extension: {filename}")

#--------------------- RUN BOT ------------------ #
async def main():
    async with bot:
        await load()
        await bot.start(TOKEN) 

asyncio.run(main())


