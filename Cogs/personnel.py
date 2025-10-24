from __future__ import annotations

import discord
from discord import app_commands, Permissions
from discord.ext import commands
from discord.ui import View, Button
from typing import Optional
import config
from config import (
    ROLE_CONFIG, MEDIA, AVAILABLE_MEDALS, MEDAL_REQUEST_PING_USER,
    has_any_role_ids, has_permission, get_required_role_mentions, get_highest_role, media_file
)

class DischargeConfirmView(View):
    def __init__(self, cog: "Personnel", member: discord.Member):
        super().__init__(timeout=60)
        self.cog = cog
        self.member = member

    @discord.ui.button(label="Confirm Discharge", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        if not isinstance(interaction.user, discord.Member) or not interaction.guild:
            await interaction.response.send_message("Something went wrong.", ephemeral=True)
            return

        # Store roles to preserve and add
        preserve_roles = [
            role for role in self.member.roles
            if role.id in ROLE_CONFIG["PRESERVE_ROLES_ON_DISCHARGE"]
        ]
        add_roles = [
            interaction.guild.get_role(role_id)
            for role_id in ROLE_CONFIG["ADD_ROLES_ON_DISCHARGE"]
        ]
        add_roles = [role for role in add_roles if role is not None]

        # Remove all roles except those to preserve
        try:
            await self.member.edit(roles=preserve_roles)
            if add_roles:
                await self.member.add_roles(*add_roles)
            
            await interaction.response.send_message("Member has been discharged.", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message(
                "Failed to modify member roles. Please check my permissions.",
                ephemeral=True
            )

        if interaction.message:
            # Disable all buttons
            for item in self.children:
                if isinstance(item, Button):
                    item.disabled = True
            await interaction.message.edit(view=self)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Discharge cancelled.", ephemeral=True)
        if interaction.message:
            # Disable all buttons
            for item in self.children:
                if isinstance(item, Button):
                    item.disabled = True
            await interaction.message.edit(view=self)

class Personnel(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="medalrequest", description="Submit a medal request")
    @app_commands.describe(medal="The medal being requested")
    @app_commands.choices(medal=[
        app_commands.Choice(name=medal, value=medal)
        for medal in AVAILABLE_MEDALS
    ])
    async def medalrequest(
        self,
        interaction: discord.Interaction,
        medal: app_commands.Choice[str]
    ):
        if not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("This command can only be used by server members.", ephemeral=True)

        if not has_permission(interaction.user, "medal_request"):
            required_roles = get_required_role_mentions("medal_request", interaction.guild)
            msg = "❌ You don't have permission to use this command."
            if required_roles:
                msg += f" Required roles: {required_roles}"
            return await interaction.response.send_message(msg, ephemeral=True)

        embed = discord.Embed(
            title="🎖️ Medal Request Submitted",
            description=f"**Application for Military Honor**\n\nA formal request has been submitted for recognition of distinguished service.",
            color=discord.Color.gold()
        )
        embed.add_field(
            name="🏅 Medal Requested", 
            value=f"**{medal.value}**",
            inline=False
        )
        embed.add_field(
            name="👤 Requesting Member", 
            value=f"{interaction.user.mention}\n*{interaction.user.display_name}*",
            inline=True
        )
        embed.add_field(
            name="📅 Request Date", 
            value=f"<t:{int(discord.utils.utcnow().timestamp())}:D>",
            inline=True
        )
        embed.add_field(
            name="📋 Status", 
            value="🟡 **Pending Review**",
            inline=True
        )
        embed.add_field(
            name="📝 Next Steps", 
            value="• Please provide evidence/proof in the thread below\n• Include detailed justification for the award\n• Command staff will review the submission",
            inline=False
        )
        embed.set_thumbnail(url=MEDIA.get("LOGO", ""))
        embed.set_footer(
            text="Medal requests require thorough documentation and command approval",
            icon_url=interaction.user.display_avatar.url
        )
        # No logo for medal request
        files = []

        if not isinstance(interaction.channel, (discord.TextChannel, discord.Thread)):
            return await interaction.response.send_message("This command can only be used in text channels.", ephemeral=True)

        # Get user to ping if configured
        ping_content = ""
        if MEDAL_REQUEST_PING_USER and interaction.guild:
            user = interaction.guild.get_member(MEDAL_REQUEST_PING_USER)
            if user:
                ping_content = user.mention

        # Send request and create thread
        message = await interaction.channel.send(content=ping_content, embed=embed, files=files)
        thread = await message.create_thread(name=f"🎖️ Medal Request - {interaction.user.display_name}", auto_archive_duration=10080)
        
        # Send detailed instructions in thread
        thread_embed = discord.Embed(
            title="📋 Evidence Submission Required",
            description="Please provide comprehensive documentation to support your medal request:",
            color=discord.Color.blue()
        )
        thread_embed.add_field(
            name="📸 Required Evidence",
            value="• Screenshots of relevant actions/achievements\n• Witness statements from other members\n• Detailed description of the qualifying event(s)",
            inline=False
        )
        thread_embed.add_field(
            name="📝 Justification",
            value="• Explain why this medal is deserved\n• Detail how your actions align with medal criteria\n• Include dates, times, and specific circumstances",
            inline=False
        )
        thread_embed.add_field(
            name="⏰ Review Process",
            value="• Command staff will review all submissions\n• Additional information may be requested\n• Decision will be communicated via this thread",
            inline=False
        )
        thread_embed.set_footer(text="Provide clear, detailed evidence for the best chance of approval")
        
        await thread.send(embed=thread_embed)

        await interaction.response.send_message("🎖️ **Medal request submitted successfully!** Please check the thread below and provide the required evidence.", ephemeral=True)

    @app_commands.command(name="discharge", description="Discharge a member")
    @app_commands.describe(reason="Reason for discharge")
    async def discharge(self, interaction: discord.Interaction, reason: str):
        if not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("This command can only be used by server members.", ephemeral=True)

        if not has_permission(interaction.user, "discharge"):
            required_roles = get_required_role_mentions("discharge", interaction.guild)
            msg = "❌ You don't have permission to use this command."
            if required_roles:
                msg += f" Required roles: {required_roles}"
            return await interaction.response.send_message(msg, ephemeral=True)

        highest_role = get_highest_role(interaction.user)
        if not highest_role:
            return await interaction.response.send_message("Could not determine member's rank.", ephemeral=True)

        embed = discord.Embed(
            title="Discharge Request",
            color=discord.Color.red()
        )
        embed.add_field(name="Member", value=interaction.user.mention, inline=True)
        embed.add_field(name="Rank", value=highest_role.name, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        # Thumbnail/logo and DR banner image via attachments
        files = []
        f1, url1 = media_file("LOGO")
        if url1 and f1:
            try:
                embed.set_thumbnail(url=url1)
                files.append(f1)
            except Exception:
                pass
        f2, url2 = media_file("DR")
        if url2 and f2:
            try:
                embed.set_image(url=url2)
                files.append(f2)
            except Exception:
                pass
        embed.set_footer(text="Thank you for your service.")

        view = DischargeConfirmView(self, interaction.user)
        await interaction.response.send_message(embed=embed, view=view, files=files, ephemeral=True)

async def setup(bot: commands.Bot):
    cog = Personnel(bot)
    await bot.add_cog(cog)

    # Defensive visibility attributes for slash commands
    try:
        for cmd_name in ('medalrequest', 'discharge'):
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