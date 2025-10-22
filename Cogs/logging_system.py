"""
NZDF Bot Logging System

This cog provides comprehensive logging for all bot command usage and errors.

Features:
- Logs all successful slash command executions with user, channel, and timestamp info
- Logs all command errors with detailed traceback information
- Pings bot admins when critical errors occur
- Professional embed formatting with thumbnails and branding
- Admin commands for testing and configuration

Setup:
1. Update COMMAND_LOG_CHANNEL in config.py with your logging channel ID
2. Restart the bot
3. Use /logstatus to verify configuration
4. Use /testlog to test the system

Admin Commands:
- /logstatus - Check current logging configuration
- /setlogchannel - Get configuration help for current channel
- /testlog - Send test logs to verify system works
"""

import discord
from discord import Permissions
from discord.ext import commands
from discord import app_commands
import datetime
from typing import Optional
import traceback
import config

class LoggingSystem(commands.Cog):
    """Comprehensive logging system for command usage and errors."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    async def get_log_channel(self) -> Optional[discord.TextChannel]:
        """Get the configured logging channel."""
        try:
            channel_id = config.CHANNEL_CONFIG["COMMAND_LOG_CHANNEL"]
            channel = self.bot.get_channel(channel_id)
            if not channel:
                print(f"[LOGGING] Channel {channel_id} not found!")
                return None
            if isinstance(channel, discord.TextChannel):
                return channel
            else:
                print(f"[LOGGING] Channel {channel_id} is not a text channel!")
                return None
        except Exception as e:
            print(f"[LOGGING] Error getting log channel: {e}")
            return None

    async def log_command_usage(self, interaction: discord.Interaction, command_name: str, success: bool = True, error: Optional[str] = None):
        """Log command usage to the designated channel."""
        channel = await self.get_log_channel()
        if not channel:
            return
            
        try:
            # Create embed for command log
            color = discord.Color.green() if success else discord.Color.red()
            status_emoji = "✅" if success else "❌"
            
            embed = discord.Embed(
                title=f"{status_emoji} Command {'Executed' if success else 'Failed'}",
                color=color,
                timestamp=datetime.datetime.utcnow()
            )
            
            # Add command info
            embed.add_field(
                name="Command",
                value=f"`/{command_name}`",
                inline=True
            )
            
            # Add user info
            user = interaction.user
            embed.add_field(
                name="User",
                value=f"{user.mention} ({user.display_name})\nID: `{user.id}`",
                inline=True
            )
            
            # Add channel info
            if interaction.guild:
                channel_name = getattr(interaction.channel, 'mention', str(interaction.channel)) if interaction.channel else 'Unknown'
                embed.add_field(
                    name="Location",
                    value=f"**Guild:** {interaction.guild.name}\n**Channel:** {channel_name}",
                    inline=True
                )
            else:
                embed.add_field(
                    name="Location",
                    value="Direct Message",
                    inline=True
                )
            
            # Add error info if failed
            if not success and error:
                embed.add_field(
                    name="Error Details",
                    value=f"```python\n{error[:1000]}{'...' if len(error) > 1000 else ''}\n```",
                    inline=False
                )
            
            # Add user avatar as thumbnail
            embed.set_thumbnail(url=user.display_avatar.url)
            
            # Add footer
            embed.set_footer(
                text=f"Command ID: {interaction.id}",
                icon_url=config.MEDIA["LOGO"]
            )
            
            await channel.send(embed=embed)
            
        except Exception as e:
            print(f"[LOGGING] Failed to log command usage: {e}")

    async def log_error_with_ping(self, interaction: discord.Interaction, command_name: str, error: Exception):
        """Log error and ping bot admins."""
        channel = await self.get_log_channel()
        if not channel:
            return
            
        try:
            # Create error embed
            embed = discord.Embed(
                title="🚨 Critical Command Error",
                color=discord.Color.dark_red(),
                timestamp=datetime.datetime.utcnow()
            )
            
            # Add command info
            embed.add_field(
                name="Failed Command",
                value=f"`/{command_name}`",
                inline=True
            )
            
            # Add user info
            user = interaction.user
            embed.add_field(
                name="User",
                value=f"{user.mention} ({user.display_name})\nID: `{user.id}`",
                inline=True
            )
            
            # Add location info
            if interaction.guild:
                channel_name = getattr(interaction.channel, 'mention', str(interaction.channel)) if interaction.channel else 'Unknown'
                embed.add_field(
                    name="Location",
                    value=f"**Guild:** {interaction.guild.name}\n**Channel:** {channel_name}",
                    inline=True
                )
            else:
                embed.add_field(
                    name="Location",
                    value="Direct Message",
                    inline=True
                )
            
            # Add error type
            embed.add_field(
                name="Error Type",
                value=f"`{type(error).__name__}`",
                inline=True
            )
            
            # Add error message
            embed.add_field(
                name="Error Message",
                value=f"```python\n{str(error)[:500]}{'...' if len(str(error)) > 500 else ''}\n```",
                inline=False
            )
            
            # Add traceback if available
            tb = traceback.format_exc()
            if tb and tb != "NoneType: None\n":
                embed.add_field(
                    name="Traceback",
                    value=f"```python\n{tb[:1000]}{'...' if len(tb) > 1000 else ''}\n```",
                    inline=False
                )
            
            # Add user avatar as thumbnail
            embed.set_thumbnail(url=user.display_avatar.url)
            
            # Add footer
            embed.set_footer(
                text=f"Error ID: {interaction.id} | Requires Admin Attention",
                icon_url=config.MEDIA["LOGO"]
            )
            
            # Create ping message for bot admins
            admin_mentions = " ".join([f"<@{admin_id}>" for admin_id in config.BOT_ADMINS])
            ping_message = f"🚨 **COMMAND ERROR ALERT** 🚨\n{admin_mentions}\n\nA critical error occurred that requires admin attention:"
            
            await channel.send(content=ping_message, embed=embed)
            
        except Exception as e:
            print(f"[LOGGING] Failed to log error with ping: {e}")

    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction: discord.Interaction, command: app_commands.Command):
        """Log successful command completions."""
        await self.log_command_usage(interaction, command.qualified_name, success=True)

    @commands.Cog.listener() 
    async def on_command_completion(self, ctx: commands.Context):
        """Log successful prefix command completions."""
        if ctx.command:
            # Skip logging for prefix commands - focus on slash commands
            pass

    # Admin command to test logging
    @app_commands.command(name="testlog", description="[ADMIN] Test the logging system")
    async def test_logging(self, interaction: discord.Interaction):
        """Test command for logging system."""
        # Check if user is bot admin
        if interaction.user.id not in config.BOT_ADMINS:
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return
            
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Test successful log
            await self.log_command_usage(interaction, "testlog", success=True)
            
            # Test error log (without actually erroring)
            test_error = Exception("This is a test error for logging system verification")
            await self.log_error_with_ping(interaction, "testlog", test_error)
            
            await interaction.followup.send("✅ Logging test completed! Check the logging channel for results.", ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Logging test failed: {str(e)}", ephemeral=True)

    @app_commands.command(name="setlogchannel", description="[ADMIN] Set the current channel as the logging channel")
    async def set_log_channel(self, interaction: discord.Interaction):
        """Set the current channel as the logging channel."""
        # Check if user is bot admin
        if interaction.user.id not in config.BOT_ADMINS:
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return
            
        if not isinstance(interaction.channel, discord.TextChannel):
            await interaction.response.send_message("❌ This command can only be used in text channels.", ephemeral=True)
            return
            
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Update the channel ID in the message (admin needs to update config manually)
            channel_id = interaction.channel.id
            
            embed = discord.Embed(
                title="📋 Logging Channel Configuration",
                description=f"To set this channel as the logging channel, update your `config.py` file:",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="Current Channel",
                value=f"{interaction.channel.mention} (ID: `{channel_id}`)",
                inline=False
            )
            
            embed.add_field(
                name="Configuration Update Required",
                value=f"```python\nCHANNEL_CONFIG: ChannelConfig = {{\n    \"CASELOG_CHANNEL\": {config.CHANNEL_CONFIG['CASELOG_CHANNEL']},\n    \"SESSION_STATUS_CHANNEL\": {config.CHANNEL_CONFIG['SESSION_STATUS_CHANNEL']},\n    \"COMMAND_LOG_CHANNEL\": {channel_id}  # ← Update this line\n}}\n```",
                inline=False
            )
            
            embed.add_field(
                name="Next Steps",
                value="1. Update the `COMMAND_LOG_CHANNEL` value in `config.py`\n2. Restart the bot\n3. Run `/testlog` to verify logging works",
                inline=False
            )
            
            embed.set_footer(text="Note: Bot restart required after config update")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to generate configuration: {str(e)}", ephemeral=True)

    @app_commands.command(name="logstatus", description="[ADMIN] Check the current logging system status")
    async def log_status(self, interaction: discord.Interaction):
        """Check the current logging system status."""
        # Check if user is bot admin
        if interaction.user.id not in config.BOT_ADMINS:
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return
            
        await interaction.response.defer(ephemeral=True)
        
        try:
            log_channel = await self.get_log_channel()
            
            embed = discord.Embed(
                title="📊 Logging System Status",
                color=discord.Color.green() if log_channel else discord.Color.red()
            )
            
            if log_channel:
                embed.add_field(
                    name="✅ Status",
                    value="Logging system is operational",
                    inline=False
                )
                embed.add_field(
                    name="📝 Log Channel",
                    value=f"{log_channel.mention} (ID: `{log_channel.id}`)",
                    inline=False
                )
                embed.add_field(
                    name="🔧 Features",
                    value="• Command usage logging\n• Error logging with admin ping\n• Automatic tracking of all slash commands\n• Test commands available",
                    inline=False
                )
            else:
                embed.add_field(
                    name="❌ Status",
                    value="Logging system not configured",
                    inline=False
                )
                embed.add_field(
                    name="🛠️ Configuration Required",
                    value=f"Current channel ID in config: `{config.CHANNEL_CONFIG.get('COMMAND_LOG_CHANNEL', 'Not set')}`\n\nUse `/setlogchannel` to get configuration instructions.",
                    inline=False
                )
            
            # Add admin list
            admin_list = ", ".join([f"<@{admin_id}>" for admin_id in config.BOT_ADMINS])
            embed.add_field(
                name="👥 Bot Admins (will be pinged on errors)",
                value=admin_list if admin_list else "None configured",
                inline=False
            )
            
            embed.set_footer(text="Logging system monitors all command activity")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to check status: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(LoggingSystem(bot))
    # Defensive: ensure admin commands are hidden from non-privileged users
    try:
        for cmd_name in ('testlog', 'setlogchannel', 'logstatus'):
            app_cmd = bot.tree.get_command(cmd_name)
            if app_cmd:
                try:
                    setattr(app_cmd, 'default_member_permissions', Permissions(manage_roles=True))
                except Exception:
                    pass
                try:
                    setattr(app_cmd, 'dm_permission', False)
                except Exception:
                    pass
    except Exception:
        pass