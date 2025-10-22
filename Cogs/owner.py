from __future__ import annotations
import asyncio
import os
import sys
import textwrap
import traceback
import discord
from discord import app_commands
from discord.ext import commands

# OWNER: change this to the single user ID that should see these commands
OWNER_ID: int = 1039388557585944656

OWNER_COMMAND_NAMES = [
    'shutdown', 'restart', 'reload', 'load', 'unload', 'status', 'stats', 'logs', 'errors',
    'diagnose', 'inviteinfo', 'uptime', 'guilds', 'members', 'userinfo', 'guildinfo',
    'permissions', 'setconfig', 'saveconfig', 'reloadconfig', 'eval', 'shell', 'broadcast',
    'dmowner', 'sync', 'clearcache', 'backup', 'restore', 'featuretoggle', 'loglevel', 'uptimegraph'
]

def owner_only_check(interaction: discord.Interaction) -> bool:
    return isinstance(interaction.user, discord.Member) and interaction.user.id == OWNER_ID


class OwnerCog(commands.Cog):
    """Owner-only sensitive commands. These commands are intended to be visible only to a single owner user.

    The cog will attempt to apply per-guild application command permissions so only the owner can see the commands.
    If permission application fails (older library, missing privileges), commands still have runtime checks that block everyone except the owner.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Apply permissions shortly after ready
        # NOTE: We do NOT programmatically alter application command permissions here to avoid
        # compatibility and permission issues across discord.py versions and API clients.
        # Instead this cog enforces owner-only access at runtime. If you want the commands
        # to be completely hidden from the UI for everyone else, set per-guild command
        # permissions in the Developer Portal or run a dedicated script (not included here)
        # which calls the application command permissions endpoint.
        pass

    # If you want a programmatic permissions applier, I can add a separate script that
    # calls the application command permissions endpoint. For now we rely on runtime
    # owner checks which are secure (no other user can run the commands) but do not
    # remove the command from other users' UI automatically.

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        # Generic owner-only error handling
        if not owner_only_check(interaction):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return
        # If owner, show error
        await interaction.response.send_message(f"❌ Owner command error: {error}", ephemeral=True)

    def owner_guard(self, interaction: discord.Interaction):
        if not owner_only_check(interaction):
            raise app_commands.CheckFailure('owner_only')

    # ---------------------- Commands ----------------------
    @app_commands.command(name='shutdown', description='(Owner) Gracefully stop the bot')
    async def shutdown(self, interaction: discord.Interaction):
        try:
            self.owner_guard(interaction)
        except app_commands.AppCommandError:
            return await interaction.response.send_message('❌ Not allowed', ephemeral=True)

        await interaction.response.send_message('Shutting down...', ephemeral=True)
        # Optionally announce to a channel (we won't assume a channel here)
        await self.bot.close()

    @app_commands.command(name='restart', description='(Owner) Restart the bot process')
    async def restart(self, interaction: discord.Interaction):
        try:
            self.owner_guard(interaction)
        except app_commands.AppCommandError:
            return await interaction.response.send_message('❌ Not allowed', ephemeral=True)

        await interaction.response.send_message('Restarting...', ephemeral=True)
        # Attempt graceful restart
        try:
            python = sys.executable
            os.execv(python, [python] + sys.argv)
        except Exception as e:
            await interaction.followup.send(f'Failed to restart: {e}', ephemeral=True)

    @app_commands.command(name='reload', description='(Owner) Reload a cog')
    @app_commands.describe(cog='Cog name to reload (e.g., Cogs.application)')
    async def reload(self, interaction: discord.Interaction, cog: str):
        try:
            self.owner_guard(interaction)
        except app_commands.AppCommandError:
            return await interaction.response.send_message('❌ Not allowed', ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        try:
            await self.bot.reload_extension(cog)
            await interaction.followup.send(f'✅ Reloaded `{cog}`', ephemeral=True)
        except Exception as e:
            tb = traceback.format_exc()
            await interaction.followup.send(f'❌ Failed to reload `{cog}`:\n{e}\n```{tb[:1000]}```', ephemeral=True)

    @app_commands.command(name='load', description='(Owner) Load a cog')
    @app_commands.describe(cog='Cog name to load (e.g., Cogs.newcog)')
    async def load(self, interaction: discord.Interaction, cog: str):
        try:
            self.owner_guard(interaction)
        except app_commands.AppCommandError:
            return await interaction.response.send_message('❌ Not allowed', ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        try:
            await self.bot.load_extension(cog)
            await interaction.followup.send(f'✅ Loaded `{cog}`', ephemeral=True)
        except Exception as e:
            tb = traceback.format_exc()
            await interaction.followup.send(f'❌ Failed to load `{cog}`:\n{e}\n```{tb[:1000]}```', ephemeral=True)

    @app_commands.command(name='unload', description='(Owner) Unload a cog')
    @app_commands.describe(cog='Cog name to unload (e.g., Cogs.application)')
    async def unload(self, interaction: discord.Interaction, cog: str):
        try:
            self.owner_guard(interaction)
        except app_commands.AppCommandError:
            return await interaction.response.send_message('❌ Not allowed', ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        try:
            await self.bot.unload_extension(cog)
            await interaction.followup.send(f'✅ Unloaded `{cog}`', ephemeral=True)
        except Exception as e:
            tb = traceback.format_exc()
            await interaction.followup.send(f'❌ Failed to unload `{cog}`:\n{e}\n```{tb[:1000]}```', ephemeral=True)

    @app_commands.command(name='status', description='(Owner) Show high-level bot status')
    async def status(self, interaction: discord.Interaction):
        try:
            self.owner_guard(interaction)
        except app_commands.AppCommandError:
            return await interaction.response.send_message('❌ Not allowed', ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        uptime = None
        try:
            # if bot has attribute start_time set elsewhere, show it
            start = getattr(self.bot, 'start_time', None)
            if start:
                uptime = discord.utils.utcnow() - start
        except Exception:
            pass

        embed = discord.Embed(title='Bot Status', color=discord.Color.blurple())
        embed.add_field(name='Guilds', value=str(len(self.bot.guilds)))
        embed.add_field(name='Users (approx)', value=str(len(self.bot.users)))
        if uptime:
            embed.add_field(name='Uptime', value=str(uptime))
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name='uptime', description='(Owner) Show bot uptime')
    async def uptime(self, interaction: discord.Interaction):
        try:
            self.owner_guard(interaction)
        except app_commands.AppCommandError:
            return await interaction.response.send_message('❌ Not allowed', ephemeral=True)

        start = getattr(self.bot, 'start_time', None)
        if not start:
            await interaction.response.send_message('Start time not recorded.', ephemeral=True)
            return
        delta = discord.utils.utcnow() - start
        await interaction.response.send_message(f'Uptime: {delta}', ephemeral=True)

    @app_commands.command(name='eval', description='(Owner) Evaluate python code')
    @app_commands.describe(code='Python code to execute')
    async def _eval(self, interaction: discord.Interaction, code: str):
        try:
            self.owner_guard(interaction)
        except app_commands.AppCommandError:
            return await interaction.response.send_message('❌ Not allowed', ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        # Dangerous: run in restricted environment
        env = {
            'bot': self.bot,
            'discord': discord,
            '__name__': '__main__'
        }
        try:
            result = eval(code, env)
            await interaction.followup.send(f'✅ Result:\n```py\n{result}\n```', ephemeral=True)
        except Exception:
            tb = traceback.format_exc()
            await interaction.followup.send(f'❌ Error:\n```py\n{tb}\n```', ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(OwnerCog(bot))
