from __future__ import annotations

import discord
from discord import app_commands, Permissions
from discord.ext import commands
import random
from config import ROLE_CONFIG, MEDIA, BEAT_ITEMS, CHANNEL_CONFIG, has_any_role_ids, has_permission, get_required_role_mentions, check_channel_restriction, get_output_channel, media_file
import config

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="beat", description="Beat someone with a random item (joke command)")
    @app_commands.describe(user="The user to beat")
    async def beat(self, interaction: discord.Interaction, user: discord.Member):
        if not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("This command can only be used by server members.", ephemeral=True)

        if not has_permission(interaction.user, "beat"):
            required_roles = get_required_role_mentions("beat", interaction.guild)
            msg = f"You don't have permission to use this command."
            if required_roles:
                msg += f" Required roles: {required_roles}"
            return await interaction.response.send_message(msg, ephemeral=True)

        item = random.choice(BEAT_ITEMS)
        
        # Simple plain text message for the joke command
        message = f"{user.mention} has been beaten by {interaction.user.mention} with {item}!"
        await interaction.response.send_message(message, allowed_mentions=discord.AllowedMentions(users=True))

    @app_commands.command(name="disciplinary", description="Issue formal disciplinary action (HICOMM only)")
    @app_commands.describe(user="The user receiving disciplinary action")
    async def disciplinary(self, interaction: discord.Interaction, user: discord.Member):
        if not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("This command can only be used by server members.", ephemeral=True)

        if not has_permission(interaction.user, "disciplinary"):
            required_roles = get_required_role_mentions("disciplinary", interaction.guild)
            msg = f"You don't have permission to use this command. (HICOMM only)"
            if required_roles:
                msg += f" Required roles: {required_roles}"
            return await interaction.response.send_message(msg, ephemeral=True)

        embed = discord.Embed(
            title="💥 DISCIPLINARY ACTION",
            description=f"**{user.display_name}** has received corrective action!",
            color=discord.Color.orange()
        )
        embed.add_field(
            name="🎯 Target",
            value=f"{user.mention}",
            inline=True
        )
        embed.add_field(
            name="⚔️ Administered by",
            value=f"{interaction.user.mention}",
            inline=True
        )
        embed.add_field(
            name="🔨 Action Type",
            value="**Verbal Warning**",
            inline=False
        )
        embed.add_field(
            name="📋 Action Result",
            value="✅ **Disciplinary measure applied**\n*Please ensure compliance with NZDF standards.*",
            inline=False
        )
        embed.set_thumbnail(url=MEDIA.get("INFRACTION", ""))
        embed.set_footer(
            text="NZDF Disciplinary System • Official Action",
            icon_url=interaction.user.display_avatar.url
        )

        await interaction.response.send_message(embed=embed, allowed_mentions=discord.AllowedMentions(users=True))

    @app_commands.command(name="inactivity", description="Send an inactivity notice")
    @app_commands.describe(user="The user to send the notice to")
    async def inactivity(self, interaction: discord.Interaction, user: discord.Member):
        if not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("This command can only be used by server members.", ephemeral=True)

        if not has_permission(interaction.user, "inactivity"):
            required_roles = get_required_role_mentions("inactivity", interaction.guild)
            msg = f"You don't have permission to use this command."
            if required_roles:
                msg += f" Required roles: {required_roles}"
            return await interaction.response.send_message(msg, ephemeral=True)

        embed = discord.Embed(
            title="Inactivity Notice",
            description=(
                "Hey,\n\n"
                "We've noticed that this ticket has been inactive for some time. To ensure we can assist you properly, "
                "please respond within 12 hours of this message. If we don't hear back from you, the ticket will be "
                "automatically closed to keep things organized.\n\n"
                "If the ticket is closed and you still need help, don't worry you can always open a new ticket at any time.\n\n"
                "We're here to help, so feel free to let us know how we can assist you further!\n\n"
                "Thank you for your understanding."
            ),
            color=discord.Color.yellow()
        )
        # No logo, no footer for inactivity notice

        if isinstance(interaction.channel, (discord.TextChannel, discord.Thread)):
            await interaction.response.send_message(embed=embed, allowed_mentions=discord.AllowedMentions(users=True))
        else:
            await interaction.response.send_message("This command can only be used in text channels.", ephemeral=True)

    @app_commands.command(name="caselog", description="Create a case log entry")
    @app_commands.describe(
        user="The user involved in the case",
        punishment="The punishment given",
        reason="The reason for the punishment"
    )
    async def caselog(self, interaction: discord.Interaction, user: discord.Member, punishment: str, reason: str):
        if not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("This command can only be used by server members.", ephemeral=True)

        if not has_permission(interaction.user, "caselog"):
            required_roles = get_required_role_mentions("caselog", interaction.guild)
            msg = f"You don't have permission to use this command."
            if required_roles:
                msg += f" Required roles: {required_roles}"
            return await interaction.response.send_message(msg, ephemeral=True)

        if not interaction.guild:
            return await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)

        # Check if command is used in the right channel
        if isinstance(interaction.channel, (discord.TextChannel, discord.Thread)):
            allowed, error_msg = check_channel_restriction("caselog", interaction.channel.id)
            if not allowed:
                return await interaction.response.send_message(error_msg, ephemeral=True)

        # Get the designated output channel (caselog always goes to caselog channel)
        output_channel = get_output_channel("caselog", interaction.guild)
        if not isinstance(output_channel, discord.TextChannel):
            return await interaction.response.send_message("Case log channel not found or not properly configured.", ephemeral=True)

        embed = discord.Embed(
            title="⚖️ Case Log",
            description=f"**User:** {user.mention}\n**Punishment:** {punishment}\n**Reason:** {reason}",
            color=discord.Color.orange()
        )
        embed.set_thumbnail(url=MEDIA.get("LOGO", ""))
        embed.set_footer(text=f"Case logged by {interaction.user.display_name}")
        
        files = []
        f, url = media_file("INFRACTION")
        if url and f:
            try:
                files.append(f)
            except Exception:
                pass

        # Send the embed and create a thread
        message = await output_channel.send(embed=embed, files=files)
        
        # Wait a tiny bit for Discord to register the message
        import asyncio
        await asyncio.sleep(0.3)
        
        # Create thread using the correct API
        try:
            thread = await message.create_thread(
                name=f"Case - {user.display_name}",
                auto_archive_duration=1440,  # 24h auto-archive
                reason="Evidence thread for case log"
            )
            await thread.send(f"Put evidence here\n-# *Logged by: {interaction.user.mention}*")
        except discord.Forbidden:
            await interaction.response.send_message("⚠️ Bot lacks permission to create threads.", ephemeral=True)
            return
        except discord.HTTPException as e:
            await interaction.response.send_message(f"⚠️ Failed to create thread: {e}", ephemeral=True)
            return

        await interaction.response.send_message(
            f"✅ Case logged for {user.mention} in <#{output_channel.id}>.", ephemeral=True
        )

async def setup(bot: commands.Bot):
    cog = Moderation(bot)
    await bot.add_cog(cog)

    # Defensive visibility attributes for slash commands
    try:
        for cmd_name in ('beat', 'disciplinary', 'inactivity', 'caselog'):
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