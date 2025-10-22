"""Owner-only cog.

Minimal single-definition OwnerCog that masks sensitive fields in logs.
"""

import io
import logging
import os
import sys
import traceback
from typing import Set

import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger("NZDF.owner")

# Replace with your owner ID(s)
OWNER_IDS: Set[int] = {1039388557585944656}


def _is_owner(interaction: discord.Interaction) -> bool:
    return getattr(interaction.user, 'id', None) in OWNER_IDS


def owner_check(interaction: discord.Interaction) -> bool:
    if not _is_owner(interaction):
        raise app_commands.CheckFailure('owner_only')
    return True


def _masked_log(interaction: discord.Interaction, *, note: str = "") -> None:
    """Log owner activity but mask sensitive command name/description."""
    uid = getattr(interaction.user, 'id', None)
    gid = getattr(interaction.guild, 'id', None) if getattr(interaction, 'guild', None) else None
    logger.info("Owner action: name=%s desc=%s user_id=%s guild_id=%s note=%s",
                "[CLASSIFIED]", "[CLASSIFIED]", uid, gid, note)


class OwnerCog(commands.Cog):
    """Small set of owner-only commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message('❌ You do not have permission to use this command.', ephemeral=True)
        else:
            await interaction.response.send_message(f'❌ Error: {error}', ephemeral=True)

    @app_commands.command(name='shutdown', description='Stop the bot (owner only)')
    @app_commands.check(owner_check)
    async def shutdown(self, interaction: discord.Interaction):
        # require explicit confirmation to avoid accidental shutdowns
        _masked_log(interaction, note='shutdown')
        await interaction.response.send_message('This will shut down the bot. Re-run with `confirm=True` to proceed.', ephemeral=True)

    @app_commands.command(name='shutdown_confirm', description='Confirm shutdown (owner only)')
    @app_commands.check(owner_check)
    async def shutdown_confirm(self, interaction: discord.Interaction, confirm: bool):
        if not confirm:
            return await interaction.response.send_message('Shutdown cancelled. Pass confirm=True to proceed.', ephemeral=True)
        _masked_log(interaction, note='shutdown_confirm')
        await interaction.response.send_message('Shutting down...', ephemeral=True)
        await self.bot.close()

    @app_commands.command(name='reload', description='Reload a cog (owner only)')
    @app_commands.describe(cog='Full cog path, e.g. Cogs.application')
    @app_commands.check(owner_check)
    async def reload(self, interaction: discord.Interaction, cog: str, confirm: bool = False):
        _masked_log(interaction, note='reload')
        if not confirm:
            return await interaction.response.send_message('Re-run with confirm=True to actually reload the cog.', ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        try:
            reload_fn = getattr(self.bot, 'reload_extension', None)
            if reload_fn is None:
                raise RuntimeError('reload_extension not available')
            reload_fn(cog)
            await interaction.followup.send(f'✅ Reloaded `{cog}`', ephemeral=True)
        except Exception:
            logger.exception('reload failed')
            await interaction.followup.send('❌ Failed to reload. [CLASSIFIED]', ephemeral=True)

    @app_commands.command(name='restart', description='Restart the bot process (owner only)')
    @app_commands.check(owner_check)
    async def restart(self, interaction: discord.Interaction, confirm: bool = False):
        _masked_log(interaction, note='restart')
        if not confirm:
            return await interaction.response.send_message('Re-run with confirm=True to actually restart the process.', ephemeral=True)
        await interaction.response.send_message('Restarting...', ephemeral=True)
        try:
            python = sys.executable
            os.execv(python, [python] + sys.argv)
        except Exception:
            logger.exception('restart failed')
            await interaction.followup.send('❌ Restart failed. [CLASSIFIED]', ephemeral=True)

    @app_commands.command(name='guilds', description='List guilds the bot is in (owner only)')
    @app_commands.check(owner_check)
    async def guilds(self, interaction: discord.Interaction):
        _masked_log(interaction, note='guilds')
        lines = [f'{g.name} (id: {g.id}) — {g.member_count} members' for g in self.bot.guilds]
        text = '\n'.join(lines) or 'No guilds'
        if len(text) > 1900:
            buf = io.BytesIO(text.encode())
            await interaction.response.send_message('Output too long; sending as file.', ephemeral=True)
            await interaction.followup.send(file=discord.File(buf, filename='guilds.txt'))
            return
        await interaction.response.send_message(f'```\n{text}\n```', ephemeral=True)

    @app_commands.command(name='dmowner', description='DM the owner (owner only)')
    @app_commands.check(owner_check)
    async def dmowner(self, interaction: discord.Interaction, message: str):
        _masked_log(interaction, note='dmowner')
        owner_id = next(iter(OWNER_IDS)) if OWNER_IDS else None
        if not owner_id:
            return await interaction.response.send_message('Owner not configured.', ephemeral=True)
        try:
            user = self.bot.get_user(owner_id) or await self.bot.fetch_user(owner_id)
            await user.send('Owner message: [CLASSIFIED]')
            await interaction.response.send_message('DM sent.', ephemeral=True)
        except Exception:
            logger.exception('dmowner failed')
            await interaction.response.send_message('❌ Failed to DM owner.', ephemeral=True)

    @app_commands.command(name='load', description='Load a cog (owner only)')
    @app_commands.describe(cog='Full cog path, e.g. Cogs.newcog')
    @app_commands.check(owner_check)
    async def load(self, interaction: discord.Interaction, cog: str, confirm: bool = False):
        _masked_log(interaction, note='load')
        if not confirm:
            return await interaction.response.send_message('Re-run with confirm=True to actually load the cog.', ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        try:
            load_fn = getattr(self.bot, 'load_extension', None)
            if load_fn is None:
                raise RuntimeError('load_extension not available')
            load_fn(cog)
            await interaction.followup.send(f'✅ Loaded `{cog}`', ephemeral=True)
        except Exception:
            logger.exception('load failed')
            await interaction.followup.send('❌ Failed to load. [CLASSIFIED]', ephemeral=True)

    @app_commands.command(name='unload', description='Unload a cog (owner only)')
    @app_commands.describe(cog='Full cog path, e.g. Cogs.application')
    @app_commands.check(owner_check)
    async def unload(self, interaction: discord.Interaction, cog: str, confirm: bool = False):
        _masked_log(interaction, note='unload')
        if not confirm:
            return await interaction.response.send_message('Re-run with confirm=True to actually unload the cog.', ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        try:
            unload_fn = getattr(self.bot, 'unload_extension', None)
            if unload_fn is None:
                raise RuntimeError('unload_extension not available')
            unload_fn(cog)
            await interaction.followup.send(f'✅ Unloaded `{cog}`', ephemeral=True)
        except Exception:
            logger.exception('unload failed')
            await interaction.followup.send('❌ Failed to unload. [CLASSIFIED]', ephemeral=True)

    @app_commands.command(name='status', description='Show high-level status (owner only)')
    @app_commands.check(owner_check)
    async def status(self, interaction: discord.Interaction):
        _masked_log(interaction, note='status')
        start = getattr(self.bot, 'start_time', None)
        uptime = (discord.utils.utcnow() - start) if start else 'unknown'
        embed = discord.Embed(title='Bot Status', color=discord.Color.blurple())
        embed.add_field(name='Guilds', value=str(len(self.bot.guilds)))
        embed.add_field(name='Users (approx)', value=str(len(self.bot.users)))
        embed.add_field(name='Uptime', value=str(uptime))
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name='uptime', description='Show bot uptime (owner only)')
    @app_commands.check(owner_check)
    async def uptime(self, interaction: discord.Interaction):
        _masked_log(interaction, note='uptime')
        start = getattr(self.bot, 'start_time', None)
        if not start:
            await interaction.response.send_message('Start time not recorded.', ephemeral=True)
            return
        delta = discord.utils.utcnow() - start
        await interaction.response.send_message(f'Uptime: {delta}', ephemeral=True)

    @app_commands.command(name='userinfo', description='Show basic info about a user (owner only)')
    @app_commands.check(owner_check)
    async def userinfo(self, interaction: discord.Interaction, user: discord.User):
        _masked_log(interaction, note='userinfo')
        embed = discord.Embed(title=f'User info — {user}', color=discord.Color.blue())
        embed.add_field(name='ID', value=str(user.id))
        embed.add_field(name='Bot?', value=str(user.bot))
        if isinstance(user, discord.Member):
            embed.add_field(name='Joined', value=str(user.joined_at))
            embed.add_field(name='Roles', value=', '.join(r.name for r in user.roles if r))
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name='commands_for', description='Show which commands a target user can run/see (owner only)')
    @app_commands.describe(target='The user to inspect')
    @app_commands.check(owner_check)
    async def commands_for(self, interaction: discord.Interaction, target: discord.User):
        """Return a list of app commands visible/usable by `target`.

        This approximates UI visibility by checking command.default_member_permissions
        and whether owner-only runtime checks would block the user. It is not
        a perfect reflection of Discord's UI rendering, but it's close enough
        for administrative inspection.
        """
        _masked_log(interaction, note='commands_for')
        bot = self.bot
        results = []
        for app_cmd in bot.tree.walk_commands():
            # skip subcommands/groups for this simple report
            name = app_cmd.name
            # check default_member_permissions attribute if present
            perms = getattr(app_cmd, 'default_member_permissions', None)
            dm_perm = getattr(app_cmd, 'dm_permission', True)

            # owner-only commands will typically have owner_check in our code; test that
            try:
                # Create a fake Interaction-like object with user=target and guild=None
                class _Fake:
                    def __init__(self, user):
                        self.user = user
                        self.guild = None

                # If the command is owner-only in our code, the simplest
                # accurate check is membership in OWNER_IDS.
                blocked = getattr(target, 'id', None) not in OWNER_IDS
                visible = True
                if perms is not None:
                    # If perms is a Permissions object, check if target has these perms is not possible here.
                    # We'll mark it as 'requires_guild_perms' when default_member_permissions is set.
                    visible = False

                results.append((name, visible and not blocked))
            except Exception:
                results.append((name, False))

        lines = [f'{n}: {"CAN" if ok else "CANNOT"}' for n, ok in results]
        text = '\n'.join(lines)
        if len(text) > 1900:
            buf = io.BytesIO(text.encode())
            await interaction.response.send_message('Output too long; sending file.', ephemeral=True)
            await interaction.followup.send(file=discord.File(buf, filename='commands_for.txt'))
            return
        # Use a single-line f-string to avoid multi-line literal issues
        await interaction.response.send_message(f'```\n{text}\n```', ephemeral=True)

    @app_commands.command(name='eval', description='Evaluate Python code (owner only)')
    @app_commands.describe(code='Python expression to evaluate')
    @app_commands.check(owner_check)
    async def _eval(self, interaction: discord.Interaction, code: str):
        _masked_log(interaction, note='eval')
        await interaction.response.defer(ephemeral=True)
        env = {'bot': self.bot, 'discord': discord, '__name__': '__main__'}
        try:
            result = eval(code, env)
            out = str(result)
            if len(out) > 1900:
                buf = io.BytesIO(out.encode())
                await interaction.followup.send('Output too long; sending as file.', ephemeral=True)
                await interaction.followup.send(file=discord.File(buf, filename='result.txt'))
                return
            await interaction.followup.send(f'✅ Result:\n```py\n{out}\n```', ephemeral=True)
        except Exception:
            tb = traceback.format_exc()
            logger.exception('eval failed')
            await interaction.followup.send('❌ Eval failed. [CLASSIFIED]', ephemeral=True)

    @app_commands.command(name='shell', description='Run a shell command on the host (owner only)')
    @app_commands.describe(command='Shell command to run')
    @app_commands.check(owner_check)
    async def shell(self, interaction: discord.Interaction, command: str):
        _masked_log(interaction, note='shell')
        await interaction.response.defer(ephemeral=True)
        try:
            import asyncio

            proc = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            out, err = await proc.communicate()
            out_text = out.decode() if out else ''
            err_text = err.decode() if err else ''
            msg = ''
            if out_text:
                msg += f'STDOUT:\n{out_text}\n'
            if err_text:
                msg += f'STDERR:\n{err_text}\n'
            if not msg:
                msg = 'No output.'
            if len(msg) > 1900:
                buf = io.BytesIO(msg.encode())
                await interaction.followup.send('Output too long; sending as file.', ephemeral=True)
                await interaction.followup.send(file=discord.File(buf, filename='shell.txt'))
                return
            await interaction.followup.send(f'```\n{msg}\n```', ephemeral=True)
        except Exception:
            tb = traceback.format_exc()
            logger.exception('shell failed')
            await interaction.followup.send('❌ Shell failed. [CLASSIFIED]', ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(OwnerCog(bot))
    # Defensive: attempt to hide owner-level commands from general UI by
    # setting default_member_permissions and dm_permission on the registered
    # app commands. This is a best-effort; for true per-guild hiding you must
    # set application command permissions in the Developer Portal or via
    # guild-specific overrides.
    try:
        for cmd in ('shutdown', 'shutdown_confirm', 'restart', 'reload', 'load', 'unload', 'status', 'uptime', 'userinfo', 'eval', 'shell', 'dmowner', 'commands_for'):
            app_cmd = bot.tree.get_command(cmd)
            if app_cmd:
                try:
                    from discord import Permissions
                    setattr(app_cmd, 'default_member_permissions', Permissions(manage_roles=True))
                except Exception:
                    pass
                try:
                    setattr(app_cmd, 'dm_permission', False)
                except Exception:
                    pass
    except Exception:
        pass

