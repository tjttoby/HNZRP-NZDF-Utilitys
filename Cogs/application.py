from __future__ import annotations
import discord
from discord import app_commands, Permissions
from discord.ext import commands
from typing import Literal
from config import ROLE_CONFIG, MEDIA, has_permission, media_file

class Application(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ An error occurred: {str(error)}", ephemeral=True)
            print(f"Error in application command: {str(error)}")

    def _build_embed(self, result: Literal["Pass", "Fail"], user: discord.Member, reason: str, notes: str, author: discord.Member) -> discord.Embed:
        if result.lower() == "pass":
            title = "✅ NZDF Application Passed"
            desc = f"{user.mention}'s application has been **approved!** 🎉"
            color = discord.Color.green()
            banner_key = "PASS"
        else:
            title = "❌ NZDF Application Failed"
            desc = f"{user.mention}'s application has been **declined.**"
            color = discord.Color.red()
            banner_key = "FAIL"
        embed = discord.Embed(title=title, description=desc, color=color)
        if reason:
            embed.add_field(name="📄 Reason", value=reason, inline=False)
        if notes:
            embed.add_field(name="🗒️ Notes", value=notes, inline=False)
        embed.add_field(name="Issued by", value=author.mention, inline=False)
        
        # Add logo as thumbnail
        embed.set_thumbnail(url=MEDIA["LOGO"])
        
        # Add banner at the bottom
        embed.set_image(url=MEDIA[banner_key])
        return embed

    # NOTE: This hides the command from users who do not have the specified guild permission.
    # We're using Manage Roles as the required permission so members without it won't see the command in the UI.
    # Assumption: roles that should be allowed to use this command have Manage Roles permission.
    @app_commands.command(name="application", description="Pass/Fail application post with details.")
    @app_commands.describe(
        result="Pass or Fail",
        user="Select the user",
        reason="Reason (shown in embed)",
        notes="Notes (shown in embed)",
    )
    @app_commands.choices(result=[
        app_commands.Choice(name="Pass", value="Pass"),
        app_commands.Choice(name="Fail", value="Fail"),
    ])
    async def application(
        self,
        interaction: discord.Interaction,
        result: app_commands.Choice[str],
        user: discord.Member,
        reason: str,
        notes: str,
    ):
        if not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("This command can only be used by server members.", ephemeral=True)

        # Check user's permissions through the permission system
        if not has_permission(interaction.user, "APPLICATION"):
            return await interaction.response.send_message("You are not allowed to use this command.", ephemeral=True)

        # Check if the channel is a text channel
        if not isinstance(interaction.channel, (discord.TextChannel, discord.Thread)):
            return await interaction.response.send_message("This command can only be used in text channels.", ephemeral=True)

        # Defer ephemerally to avoid public "X used /application"
        await interaction.response.defer(ephemeral=True)

        # Type assertion for result.value as Literal["Pass", "Fail"]
        result_value = "Pass" if result.value == "Pass" else "Fail"
        embed = self._build_embed(result_value, user, reason, notes, interaction.user)

        # Store channel reference to ensure it exists throughout the interaction
        channel = interaction.channel
        
        # Since we're now using URL links, no files need to be attached
        # Send embed only (no usage log above)
        await channel.send(embed=embed)

        # Optionally inform the invoker ephemerally
        await interaction.followup.send("Application posted.", ephemeral=True)

async def setup(bot: commands.Bot):
    cog = Application(bot)
    await bot.add_cog(cog)

    # Defensive: ensure the app command has the intended visibility attributes set.
    # Some discord.py/backends don't accept `default_member_permissions` or `dm_permission`
    # in the decorator signature; set them directly on the command object after registration.
    try:
        app_cmd = bot.tree.get_command('application')
        if app_cmd:
            # require Manage Roles so users without that permission won't see the command in the UI
            try:
                setattr(app_cmd, 'default_member_permissions', Permissions(manage_roles=True))
            except Exception:
                pass
            try:
                setattr(app_cmd, 'dm_permission', False)
            except Exception:
                pass
    except Exception:
        # Non-fatal - command visibility will fall back to permission checks at runtime
        pass