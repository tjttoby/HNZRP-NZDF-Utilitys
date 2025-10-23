"""Owner-only cog.

Minimal single-definition OwnerCog that masks sensitive fields in logs.
"""

import io
import logging
import os
import sys
import traceback
from typing import Set
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
import config
from Cogs.logging_system import LoggingSystem # Import LoggingSystem

logger = logging.getLogger("NZDF.owner")

# Replace with your owner ID(s)
OWNER_IDS: Set[int] = {123456789012345678}  # Replace with actual owner Discord user ID

# Names of commands that should be owner-only in the UI
OWNER_COMMAND_NAMES = {
    'shutdown', 'shutdown_confirm', 'restart', 'reload', 'load', 'unload',
    'status', 'uptime', 'userinfo', 'eval', 'shell', 'dmowner', 'commands_for',
    'guilds', 'list_cogs', 'logs', 'sync', 'clear_commands'
}

# Describe available owner commands and whether they require additional input via a modal.
# Each spec is: description, fields (list). Field: name, label, style ('short'|'paragraph'), type ('str'|'bool'|'user')
COMMAND_SPECS = {
    'guilds': {'desc': 'List guilds the bot is in', 'fields': []},
    'status': {'desc': 'Show high-level status', 'fields': []},
    'uptime': {'desc': 'Show bot uptime', 'fields': []},
    'list_cogs': {'desc': 'List all available and loaded cogs', 'fields': []},
    'logs': {'desc': 'Get recent bot logs (default 50 lines)', 'fields': [
        {'name': 'lines', 'label': 'Number of lines (default 50)', 'style': 'short', 'type': 'str'}
    ]},
    'sync': {'desc': 'Sync slash commands globally or to a guild', 'fields': [
        {'name': 'guild_id', 'label': 'Guild ID (leave empty for global sync)', 'style': 'short', 'type': 'str'}
    ]},
    'clear_commands': {'desc': 'Clear all slash commands globally or from a guild', 'fields': [
        {'name': 'guild_id', 'label': 'Guild ID (leave empty for global clear)', 'style': 'short', 'type': 'str'}
    ]},
    'shutdown_confirm': {'desc': 'Confirm shutdown (requires confirm text)', 'fields': [
        {'name': 'confirm', 'label': 'Type YES to confirm shutdown', 'style': 'short', 'type': 'bool'}
    ]},
    'restart': {'desc': 'Restart the bot process (requires confirm)', 'fields': [
        {'name': 'confirm', 'label': 'Type YES to confirm restart', 'style': 'short', 'type': 'bool'}
    ]},
    'reload': {'desc': 'Reload a cog (requires cog path and confirm)', 'fields': [
        {'name': 'cog', 'label': 'Cog path (e.g. Cogs.application)', 'style': 'short', 'type': 'str'},
        {'name': 'confirm', 'label': 'Type YES to confirm reload', 'style': 'short', 'type': 'bool'}
    ]},
    'load': {'desc': 'Load a cog (requires cog path and confirm)', 'fields': [
        {'name': 'cog', 'label': 'Cog path (e.g. Cogs.newcog)', 'style': 'short', 'type': 'str'},
        {'name': 'confirm', 'label': 'Type YES to confirm load', 'style': 'short', 'type': 'bool'}
    ]},
    'unload': {'desc': 'Unload a cog (requires cog path and confirm)', 'fields': [
        {'name': 'cog', 'label': 'Cog path (e.g. Cogs.application)', 'style': 'short', 'type': 'str'},
        {'name': 'confirm', 'label': 'Type YES to confirm unload', 'style': 'short', 'type': 'bool'}
    ]},
    'userinfo': {'desc': 'Show basic info about a user (provide user id or mention)', 'fields': [
        {'name': 'user', 'label': 'User ID or mention', 'style': 'short', 'type': 'user'}
    ]},
    'dmowner': {'desc': 'DM the owner (provide message)', 'fields': [
        {'name': 'message', 'label': 'Message to send to owner', 'style': 'paragraph', 'type': 'str'}
    ]},
    'commands_for': {'desc': 'Show which commands a target user can run/see (provide user id/mention)', 'fields': [
        {'name': 'target', 'label': 'Target user ID or mention', 'style': 'short', 'type': 'user'}
    ]},
    'eval': {'desc': 'Evaluate Python code (provide expression/code)', 'fields': [
        {'name': 'code', 'label': 'Python code to evaluate', 'style': 'paragraph', 'type': 'str'}
    ]},
    'shell': {'desc': 'Run a shell command (provide command to run)', 'fields': [
        {'name': 'command', 'label': 'Shell command to run', 'style': 'paragraph', 'type': 'str'}
    ]}
}

# Commands considered sensitive and which should require explicit confirmation
SENSITIVE_COMMANDS = {'shutdown_confirm', 'restart', 'reload', 'load', 'unload', 'eval', 'shell', 'dmowner', 'clear_commands'}


    


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

    async def _maybe_log(self, interaction: discord.Interaction, command_name: str, success: bool = True, error: Optional[str] = None):
        """Call the LoggingSystem cog to record the command unless configured to ignore it."""
        try:
            ignored = getattr(config, 'IGNORED_COMMANDS', None) or []
            if command_name in ignored:
                return
            log_cog = self.bot.get_cog('LoggingSystem')
            if log_cog and isinstance(log_cog, LoggingSystem) and hasattr(log_cog, 'log_command_usage'):
                await log_cog.log_command_usage(interaction, command_name, success=success, error=error)
        except Exception:
            logger.exception('failed to call log cog')

    # --- Implementation helpers (callable by UI and by app command wrappers) ---
    async def _impl_guilds(self, interaction: discord.Interaction):
        _masked_log(interaction, note='guilds')
        lines = [f'{g.name} (id: {g.id}) — {g.member_count} members' for g in self.bot.guilds]
        text = '\n'.join(lines) or 'No guilds'
        if len(text) > 1900:
            buf = io.BytesIO(text.encode())
            await interaction.response.send_message('Output too long; sending as file.', ephemeral=True)
            await interaction.followup.send(file=discord.File(buf, filename='guilds.txt'))
            return
        await interaction.response.send_message(f'```\n{text}\n```', ephemeral=True)

    async def _impl_status(self, interaction: discord.Interaction):
        _masked_log(interaction, note='status')
        start = getattr(self.bot, 'start_time', None)
        uptime = (discord.utils.utcnow() - start) if start else 'unknown'
        embed = discord.Embed(title='Bot Status', color=discord.Color.blurple())
        embed.add_field(name='Guilds', value=str(len(self.bot.guilds)))
        embed.add_field(name='Users (approx)', value=str(len(self.bot.users)))
        embed.add_field(name='Uptime', value=str(uptime))
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def _impl_uptime(self, interaction: discord.Interaction):
        _masked_log(interaction, note='uptime')
        start = getattr(self.bot, 'start_time', None)
        if not start:
            await interaction.response.send_message('Start time not recorded.', ephemeral=True)
            return
        delta = discord.utils.utcnow() - start
        await interaction.response.send_message(f'Uptime: {delta}', ephemeral=True)

    async def _impl_shutdown_confirm(self, interaction: discord.Interaction, confirm: bool):
        if not confirm:
            return await interaction.response.send_message('Shutdown cancelled. Pass confirm=True to proceed.', ephemeral=True)
        _masked_log(interaction, note='shutdown_confirm')
        await interaction.response.send_message('Shutting down...', ephemeral=True)
        await self.bot.close()

    async def _impl_restart(self, interaction: discord.Interaction, confirm: bool = False):
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

    async def _impl_reload(self, interaction: discord.Interaction, cog: str, confirm: bool = False):
        _masked_log(interaction, note='reload')
        if not confirm:
            return await interaction.response.send_message('Re-run with confirm=True to actually reload the cog.', ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        try:
            await self.bot.reload_extension(cog)
            await interaction.followup.send(f'✅ Successfully reloaded `{cog}`', ephemeral=True)
        except Exception as e:
            logger.exception('reload failed')
            await interaction.followup.send(f'❌ Failed to reload `{cog}`: {str(e)}', ephemeral=True)

    async def _impl_load(self, interaction: discord.Interaction, cog: str, confirm: bool = False):
        _masked_log(interaction, note='load')
        if not confirm:
            return await interaction.response.send_message('Re-run with confirm=True to actually load the cog.', ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        try:
            await self.bot.load_extension(cog)
            await interaction.followup.send(f'✅ Successfully loaded `{cog}`', ephemeral=True)
        except Exception as e:
            logger.exception('load failed')
            await interaction.followup.send(f'❌ Failed to load `{cog}`: {str(e)}', ephemeral=True)

    async def _impl_unload(self, interaction: discord.Interaction, cog: str, confirm: bool = False):
        _masked_log(interaction, note='unload')
        if not confirm:
            return await interaction.response.send_message('Re-run with confirm=True to actually unload the cog.', ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        try:
            await self.bot.unload_extension(cog)
            await interaction.followup.send(f'✅ Successfully unloaded `{cog}`', ephemeral=True)
        except Exception as e:
            logger.exception('unload failed')
            await interaction.followup.send(f'❌ Failed to unload `{cog}`: {str(e)}', ephemeral=True)

    async def _impl_list_cogs(self, interaction: discord.Interaction):
        """List all available and loaded cogs."""
        _masked_log(interaction, note='list_cogs')
        
        # Get loaded cogs
        loaded = list(self.bot.extensions.keys())
        
        # Get available cogs by scanning Cogs directory
        import os
        available = []
        cogs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Cogs')
        if os.path.exists(cogs_dir):
            for file in os.listdir(cogs_dir):
                if file.endswith('.py') and not file.startswith('__'):
                    available.append(f"Cogs.{file[:-3]}")
        
        embed = discord.Embed(title='🔧 Cog Management', color=discord.Color.blue())
        
        if loaded:
            loaded_list = '\n'.join(f"✅ `{cog}`" for cog in sorted(loaded))
            embed.add_field(name='Loaded Cogs', value=loaded_list, inline=False)
        
        if available:
            unloaded = [cog for cog in available if cog not in loaded]
            if unloaded:
                unloaded_list = '\n'.join(f"❌ `{cog}`" for cog in sorted(unloaded))
                embed.add_field(name='Available (Unloaded) Cogs', value=unloaded_list, inline=False)
        
        embed.set_footer(text=f"Total: {len(available)} available, {len(loaded)} loaded")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def _impl_dmowner(self, interaction: discord.Interaction, message: str):
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

    async def _impl_userinfo(self, interaction: discord.Interaction, user: discord.User):
        _masked_log(interaction, note='userinfo')
        embed = discord.Embed(title=f'User info — {user}', color=discord.Color.blue())
        embed.add_field(name='ID', value=str(user.id))
        embed.add_field(name='Bot?', value=str(user.bot))
        if isinstance(user, discord.Member):
            embed.add_field(name='Joined', value=str(user.joined_at))
            embed.add_field(name='Roles', value=', '.join(r.name for r in user.roles if r))
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def _impl_commands_for(self, interaction: discord.Interaction, target: discord.User):
        _masked_log(interaction, note='commands_for')
        bot = self.bot
        results = []
        for app_cmd in bot.tree.walk_commands():
            name = app_cmd.name
            perms = getattr(app_cmd, 'default_member_permissions', None)
            # owner-only commands will typically have owner_check; approximate
            blocked = getattr(target, 'id', None) not in OWNER_IDS
            visible = True
            if perms is not None:
                visible = False
            results.append((name, visible and not blocked))
        lines = [f'{n}: {"CAN" if ok else "CANNOT"}' for n, ok in results]
        text = '\n'.join(lines)
        if len(text) > 1900:
            buf = io.BytesIO(text.encode())
            await interaction.response.send_message('Output too long; sending file.', ephemeral=True)
            await interaction.followup.send(file=discord.File(buf, filename='commands_for.txt'))
            return
        await interaction.response.send_message(f'```\n{text}\n```', ephemeral=True)

    async def _impl_eval(self, interaction: discord.Interaction, code: str):
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

    async def _impl_shell(self, interaction: discord.Interaction, command: str):
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

    async def _impl_logs(self, interaction: discord.Interaction, lines: int = 50):
        """Get recent bot logs."""
        _masked_log(interaction, note='logs')
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Try to get logs from the logging system if available
            log_cog = self.bot.get_cog('LoggingSystem')
            if log_cog and hasattr(log_cog, '_recent_log_lines'):
                recent_logs = list(getattr(log_cog, '_recent_log_lines', []))
                if recent_logs:
                    # Get last N lines
                    log_lines = recent_logs[-lines:] if len(recent_logs) > lines else recent_logs
                    log_text = '\n'.join(log_lines)
                    
                    if len(log_text) > 1900:
                        buf = io.BytesIO(log_text.encode())
                        await interaction.followup.send(f'Recent {len(log_lines)} log lines (file):', ephemeral=True)
                        await interaction.followup.send(file=discord.File(buf, filename='recent_logs.txt'))
                    else:
                        await interaction.followup.send(f'```\n{log_text}\n```', ephemeral=True)
                else:
                    await interaction.followup.send('No recent logs available.', ephemeral=True)
            else:
                await interaction.followup.send('Logging system not available.', ephemeral=True)
        except Exception as e:
            logger.exception('logs failed')
            await interaction.followup.send(f'❌ Failed to get logs: {str(e)}', ephemeral=True)

    async def _impl_sync(self, interaction: discord.Interaction, guild_id: Optional[int] = None):
        """Sync slash commands."""
        _masked_log(interaction, note='sync')
        await interaction.response.defer(ephemeral=True)
        
        try:
            if guild_id:
                guild = self.bot.get_guild(guild_id)
                if not guild:
                    await interaction.followup.send(f'❌ Guild {guild_id} not found.', ephemeral=True)
                    return
                synced = await self.bot.tree.sync(guild=guild)
                await interaction.followup.send(f'✅ Synced {len(synced)} commands to guild {guild.name} ({guild_id})', ephemeral=True)
            else:
                synced = await self.bot.tree.sync()
                await interaction.followup.send(f'✅ Synced {len(synced)} commands globally', ephemeral=True)
        except Exception as e:
            logger.exception('sync failed')
            await interaction.followup.send(f'❌ Failed to sync commands: {str(e)}', ephemeral=True)

    async def _impl_clear_commands(self, interaction: discord.Interaction, guild_id: Optional[int] = None):
        """Clear all slash commands."""
        _masked_log(interaction, note='clear_commands')
        await interaction.response.defer(ephemeral=True)
        
        try:
            if guild_id:
                guild = self.bot.get_guild(guild_id)
                if not guild:
                    await interaction.followup.send(f'❌ Guild {guild_id} not found.', ephemeral=True)
                    return
                self.bot.tree.clear_commands(guild=guild)
                await self.bot.tree.sync(guild=guild)
                await interaction.followup.send(f'✅ Cleared commands for guild {guild.name} ({guild_id})', ephemeral=True)
            else:
                self.bot.tree.clear_commands(guild=None)
                await self.bot.tree.sync()
                await interaction.followup.send('✅ Cleared all global commands', ephemeral=True)
        except Exception as e:
            logger.exception('clear_commands failed')
            await interaction.followup.send(f'❌ Failed to clear commands: {str(e)}', ephemeral=True)

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message('❌ You do not have permission to use this command.', ephemeral=True)
        else:
            await interaction.response.send_message(f'❌ Error: {error}', ephemeral=True)

    # Note: individual app command decorators removed. All owner actions are available
    # through the `/x panel` UI to reduce UI clutter. The implementation helpers
    # are still callable directly from code.

    # reload via panel

    # restart via panel

    # guilds via panel

    # dmowner via panel

    # load via panel

    # unload via panel

    # status via panel

    # uptime via panel

    # userinfo via panel

    # commands_for via panel
    @app_commands.describe(target='The user to inspect')
    async def commands_for(self, interaction: discord.Interaction, target: discord.User):
        """Return a list of app commands visible/usable by `target`.

        This approximates UI visibility by checking command.default_member_permissions
        and whether owner-only runtime checks would block the user. It is not
        a perfect reflection of Discord's UI rendering, but it's close enough
        for administrative inspection.
        """
        await self._impl_commands_for(interaction, target)

    # apply_owner_ui left as an app command because it's an administrative convenience
    @app_commands.command(name='apply_owner_ui', description='Apply per-guild permissions so owner commands are hidden for others')
    @app_commands.describe(guild='Optional guild ID to apply to (defaults to all guilds the bot is in)')
    @app_commands.check(owner_check)
    async def apply_owner_ui(self, interaction: discord.Interaction, guild: Optional[int] = None, dry_run: bool = False):
        """Best-effort: set application command permissions per guild so only OWNER_IDS can use/see owner commands.

        This uses the REST API to set per-command guild permissions. It requires the bot to be in the guild and
        the bot's application to be available. Some hosts/backends may not support setting permissions.
        """
        _masked_log(interaction, note='apply_owner_ui')
        await interaction.response.defer(ephemeral=True)
        try:
            app_info = await self.bot.application_info()
            app_id = app_info.id
        except Exception:
            # Fallback
            app_id = getattr(self.bot, 'application_id', None) or getattr(self.bot.user, 'id', None)

        from discord.http import Route

        # Default: if invoked inside a guild and no guild param provided, operate on that guild only.
        if guild is None and interaction.guild is not None:
            guilds = [interaction.guild]
        else:
            guilds = [g for g in self.bot.guilds if (guild is None or g.id == guild)]
        if not guilds:
            await interaction.followup.send('No matching guilds found (bot not in specified guild?).', ephemeral=True)
            return

        failures = []
        successes = []
        for g in guilds:
            try:
                # GET guild application commands
                route_get = Route('GET', '/applications/{application_id}/guilds/{guild_id}/commands', application_id=app_id, guild_id=g.id)
                cmds = await self.bot.http.request(route_get)
                for cmd in cmds:
                    name = cmd.get('name')
                    cmd_id = cmd.get('id')
                    if not name or not cmd_id:
                        continue
                    if name not in OWNER_COMMAND_NAMES:
                        continue
                    if dry_run:
                        # only record what would be changed
                        continue
                    # Build permission entries for owner user IDs and roles
                    perms = []
                    owner_roles = getattr(config, 'OWNER_ROLES', []) or []
                    for oid in OWNER_IDS:
                        perms.append({
                            'id': str(oid),
                            'type': 2,  # 2 = USER
                            'permission': True
                        })
                    for rid in owner_roles:
                        perms.append({
                            'id': str(rid),
                            'type': 1,  # 1 = ROLE
                            'permission': True
                        })
                    route_put = Route('PUT', '/applications/{application_id}/guilds/{guild_id}/commands/{command_id}/permissions', application_id=app_id, guild_id=g.id, command_id=cmd_id)
                    await self.bot.http.request(route_put, json={'permissions': perms})
                successes.append(g.id)
            except Exception as e:
                logger.exception('apply_owner_ui failed for guild %s', g.id)
                failures.append((g.id, str(e)))

        msg = f'Applied owner UI permissions to guilds: {successes}. Failures: {failures}'
        await interaction.followup.send(msg, ephemeral=True)

    # eval via panel

    # shell via panel


async def setup(bot: commands.Bot) -> None:
    cog = OwnerCog(bot)
    await bot.add_cog(cog)
    # Register the umbrella app group so `/x` is available and can call into the cog's impl methods
    try:
        bot.tree.add_command(OwnerAdmin(cog))
    except Exception:
        # best-effort; ignore if it fails in some environments
        pass
    # Remove any legacy/top-level owner commands so only `/x` remains
    try:
        for name in list(OWNER_COMMAND_NAMES):
            # skip the panel/apply helper
            if name in ('apply_owner_ui', 'x'):
                continue
            existing = bot.tree.get_command(name)
            if existing:
                try:
                    bot.tree.remove_command(name)
                except Exception:
                    # best-effort; continue
                    pass
    except Exception:
        pass
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


class _ExecuteView(discord.ui.View):
    def __init__(self, cog: OwnerCog, command_name: str):
        super().__init__(timeout=60)
        self.cog = cog
        self.command_name = command_name

    @discord.ui.button(label="Execute", style=discord.ButtonStyle.danger)
    async def execute(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Only owner allowed
        if getattr(interaction.user, 'id', None) not in OWNER_IDS:
            return await interaction.response.send_message('Not allowed', ephemeral=True)

        cmd = self.command_name
        # map to functions that take (interaction) or note if args required
        argless = {'guilds', 'status', 'uptime'}
        if cmd in argless:
            await interaction.response.defer(ephemeral=True)
            try:
                fn = getattr(self.cog, f'_impl_{cmd}', None)
                if fn is None:
                    raise RuntimeError('implementation missing')
                await fn(interaction)
            except Exception:
                logger.exception('panel exec failed')
                await interaction.followup.send('Execution failed. [CLASSIFIED]', ephemeral=True)
        else:
            # For commands requiring args, instruct user to use /x <command>
            await interaction.response.send_message(f'This command requires arguments; please use the panel to run `/x panel` and submit required inputs.', ephemeral=True)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Cancelled.', ephemeral=True)


class OwnerAdmin(app_commands.Group):
    def __init__(self, cog: OwnerCog):
        super().__init__(name='x', description='Owner umbrella for admin commands')
        self.cog = cog

    @app_commands.command(name='panel', description='Open a compact panel with owner commands')
    @app_commands.check(owner_check)
    async def panel(self, interaction: discord.Interaction):
        options = [discord.SelectOption(label=name, value=name) for name in sorted(OWNER_COMMAND_NAMES)]
        # Build a config embed with descriptions for each owner command
        embed = discord.Embed(title='Owner Commands', description='Select a command from the dropdown below. Commands that require additional input will open a modal.', color=discord.Color.dark_blue())
        for name in sorted(OWNER_COMMAND_NAMES):
            spec = COMMAND_SPECS.get(name, {'desc': '(no description)'})
            embed.add_field(name=name, value=spec['desc'], inline=False)

        options = [discord.SelectOption(label=name, value=name, description=COMMAND_SPECS.get(name, {}).get('desc', '')) for name in sorted(OWNER_COMMAND_NAMES)]

        # Modal factory
        def make_modal(command_name: str, fields: list):
            # Dynamically create a modal with appropriate TextInput fields
            class _DynModal(discord.ui.Modal, title=f'Fill inputs for {command_name}'):
                # type-hints for dynamic attributes to satisfy static analysis
                modal_cog: 'OwnerCog'
                _values: dict

                def __init__(self):
                    super().__init__()
                    self._values = {}
                    for f in fields:
                        style = discord.TextStyle.long if f.get('style') == 'paragraph' else discord.TextStyle.short
                        ti = discord.ui.TextInput(label=f.get('label', f['name']), style=style, required=True)
                        setattr(self, f['name'], ti)
                        self.add_item(ti)

                async def on_submit(self, modal_inter: discord.Interaction):
                    # acknowledge modal immediately to avoid timeout
                    try:
                        await modal_inter.response.defer(ephemeral=True)
                    except Exception:
                        pass
                    # collect values and call appropriate impl
                    for f in fields:
                        self._values[f['name']] = getattr(self, f['name']).value
                    # Dispatch to handler
                    try:
                        # special conversions and explicit branching
                        if command_name in ('reload', 'load', 'unload'):
                            cogpath = self._values.get('cog')
                            confirm_raw = self._values.get('confirm', '')
                            confirm = confirm_raw.strip().lower() in ('yes', 'y', 'true', '1')
                            if not cogpath:
                                await modal_inter.response.send_message('Cog path not provided.', ephemeral=True)
                                return
                            if command_name == 'reload':
                                await self.modal_cog._impl_reload(modal_inter, str(cogpath), confirm)
                                await self.modal_cog._maybe_log(modal_inter, 'reload')
                            elif command_name == 'load':
                                await self.modal_cog._impl_load(modal_inter, str(cogpath), confirm)
                                await self.modal_cog._maybe_log(modal_inter, 'load')
                            elif command_name == 'unload':
                                await self.modal_cog._impl_unload(modal_inter, str(cogpath), confirm)
                                await self.modal_cog._maybe_log(modal_inter, 'unload')
                        elif command_name == 'shutdown_confirm':
                            confirm_raw = self._values.get('confirm', '')
                            confirm = confirm_raw.strip().lower() in ('yes', 'y', 'true', '1')
                            await self.modal_cog._impl_shutdown_confirm(modal_inter, confirm)
                            await self.modal_cog._maybe_log(modal_inter, 'shutdown_confirm')
                        elif command_name == 'restart':
                            confirm_raw = self._values.get('confirm', '')
                            confirm = confirm_raw.strip().lower() in ('yes', 'y', 'true', '1')
                            await self.modal_cog._impl_restart(modal_inter, confirm)
                            await self.modal_cog._maybe_log(modal_inter, 'restart')
                        elif command_name == 'dmowner':
                            msg = self._values.get('message', '')
                            await self.modal_cog._impl_dmowner(modal_inter, msg)
                            await self.modal_cog._maybe_log(modal_inter, 'dmowner')
                        elif command_name == 'commands_for':
                            t = self._values.get('target')
                            digits = ''.join(ch for ch in (t or '') if ch.isdigit())
                            if not digits:
                                await modal_inter.response.send_message('Could not resolve user.', ephemeral=True)
                                return
                            try:
                                user = await modal_inter.client.fetch_user(int(digits))
                            except Exception:
                                await modal_inter.response.send_message('Could not resolve user.', ephemeral=True)
                                return
                            await self.modal_cog._impl_commands_for(modal_inter, user)
                            await self.modal_cog._maybe_log(modal_inter, 'commands_for')
                        elif command_name == 'userinfo':
                            t = self._values.get('user')
                            digits = ''.join(ch for ch in (t or '') if ch.isdigit())
                            if not digits:
                                await modal_inter.response.send_message('Could not resolve user.', ephemeral=True)
                                return
                            try:
                                user = await modal_inter.client.fetch_user(int(digits))
                            except Exception:
                                await modal_inter.response.send_message('Could not resolve user.', ephemeral=True)
                                return
                            await self.modal_cog._impl_userinfo(modal_inter, user)
                            await self.modal_cog._maybe_log(modal_inter, 'userinfo')
                        elif command_name == 'eval':
                            code = self._values.get('code', '')
                            # require extra confirmation for eval
                            confirm_view = ConfirmView(self.modal_cog, command_name, {'code': code})
                            await modal_inter.response.send_message('Please confirm evaluation (sensitive).', view=confirm_view, ephemeral=True)
                        elif command_name == 'shell':
                            cmd = self._values.get('command', '')
                            # require extra confirmation for shell
                            confirm_view = ConfirmView(self.modal_cog, command_name, {'command': cmd})
                            await modal_inter.response.send_message('Please confirm shell execution (sensitive).', view=confirm_view, ephemeral=True)
                        else:
                            await modal_inter.response.send_message('Unknown command', ephemeral=True)
                    except Exception:
                        logger.exception('modal execution failed')
                        await modal_inter.response.send_message('Execution failed. [CLASSIFIED]', ephemeral=True)

            # attach reference to cog after creation
            m = _DynModal()
            m.modal_cog = self.cog
            return m

        class _CommandSelect(discord.ui.Select):
            def __init__(self, cog: OwnerCog):
                self.cog = cog
                super().__init__(placeholder='Choose owner command', min_values=1, max_values=1, options=options)

            async def callback(self, interaction: discord.Interaction):
                logger.info('OwnerAdmin: select callback invoked by %s', getattr(interaction.user, 'id', None))
                choice = self.values[0]
                spec = COMMAND_SPECS.get(choice, {})
                fields = spec.get('fields', [])
                # If no extra fields, execute immediately using impl
                if not fields:
                    # if sensitive, show confirmation view
                    if choice in SENSITIVE_COMMANDS:
                        logger.info('OwnerAdmin: %s is sensitive; asking confirm', choice)
                        confirm_view = ConfirmView(self.cog, choice, {})
                        await interaction.response.send_message(f'Please confirm {choice} (sensitive).', view=confirm_view, ephemeral=True)
                        return
                    await interaction.response.defer(ephemeral=True)
                    try:
                        handler = getattr(self.cog, f'_impl_{choice}', None)
                        if handler is None:
                            raise RuntimeError('implementation missing')
                        await handler(interaction)
                    except Exception:
                        logger.exception('panel exec failed')
                        await interaction.followup.send('Execution failed. [CLASSIFIED]', ephemeral=True)
                    return
                # otherwise open modal
                logger.info('OwnerAdmin: opening modal for %s', choice)
                modal = make_modal(choice, fields)
                await interaction.response.send_modal(modal)

        # instantiate the select and send the panel view (kept inside the panel method scope)
        try:
            sel = _CommandSelect(self.cog)
            view = discord.ui.View()
            view.add_item(sel)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        except Exception:
            logger.exception('failed to send panel response')
            # Ensure we always acknowledge the interaction to avoid 'Application did not respond'
            try:
                await interaction.response.send_message('❌ Failed to open panel. [CLASSIFIED]', ephemeral=True)
            except Exception:
                # If we can't send (maybe already responded), attempt a followup
                try:
                    await interaction.followup.send('❌ Failed to open panel. [CLASSIFIED]', ephemeral=True)
                except Exception:
                    logger.exception('also failed to followup after panel send failure')


class ConfirmView(discord.ui.View):
    def __init__(self, cog: OwnerCog, command_name: str, payload: dict):
        super().__init__(timeout=60)
        self.cog = cog
        self.command_name = command_name
        self.payload = payload

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if getattr(interaction.user, 'id', None) not in OWNER_IDS:
            return await interaction.response.send_message('Not allowed', ephemeral=True)
        try:
            # Defer to avoid the 3s interaction timeout while performing impl work
            await interaction.response.defer(ephemeral=True)
            # dispatch based on command_name
            if self.command_name == 'eval':
                await self.cog._impl_eval(interaction, self.payload.get('code', ''))
            elif self.command_name == 'shell':
                await self.cog._impl_shell(interaction, self.payload.get('command', ''))
            elif self.command_name == 'shutdown_confirm':
                await self.cog._impl_shutdown_confirm(interaction, True)
            elif self.command_name == 'restart':
                await self.cog._impl_restart(interaction, True)
            elif self.command_name in ('reload', 'load', 'unload'):
                cogpath = self.payload.get('cog')
                confirm = True
                if not cogpath:
                    await interaction.response.send_message('Cog path not provided.', ephemeral=True)
                    return
                if self.command_name == 'reload':
                    await self.cog._impl_reload(interaction, str(cogpath), confirm)
                elif self.command_name == 'load':
                    await self.cog._impl_load(interaction, str(cogpath), confirm)
                elif self.command_name == 'unload':
                    await self.cog._impl_unload(interaction, str(cogpath), confirm)
            elif self.command_name == 'dmowner':
                await self.cog._impl_dmowner(interaction, self.payload.get('message', ''))
            else:
                await interaction.response.send_message('Unknown or unhandled command', ephemeral=True)
        except Exception:
            logger.exception('confirmation execution failed')
            await interaction.response.send_message('Execution failed. [CLASSIFIED]', ephemeral=True)

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Cancelled.', ephemeral=True)

    # The OwnerAdmin group only exposes the `panel` subcommand. All other owner actions
    # are available exclusively via the panel UI (modals/confirmation flow).
