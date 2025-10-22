from __future__ import annotations

import discord
from discord import app_commands, Permissions
from discord.ext import commands
from discord.ui import View, Button
from typing import Optional
from config import (
    ROLE_CONFIG, MEDIA, AVAILABLE_MEDALS, MEDAL_REQUEST_PING_USER,
    has_any_role_ids, get_highest_role, media_file
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

    @app_commands.command(
        name="medalrequest",
        description="Submit a medal request",
        default_member_permissions=Permissions(manage_roles=True),
        dm_permission=False,
    )
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

        if not has_any_role_ids(interaction.user, ROLE_CONFIG["MEDAL_REQUEST_ALLOWED_ROLES"]):
            return await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

        embed = discord.Embed(
            title="Medal Request",
            description=f"Medal: {medal.value}",
            color=discord.Color.blue()
        )
        embed.add_field(name="Requested By", value=interaction.user.mention)
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
        message = await interaction.channel.send(embed=embed, files=files)
        thread = await message.create_thread(name=f"Medal Request - {interaction.user.name}", auto_archive_duration=10080)
        await thread.send("Please provide proof here.")

        await interaction.response.send_message("Medal request submitted!", ephemeral=True)

    @app_commands.command(
        name="discharge",
        description="Discharge a member",
        default_member_permissions=Permissions(manage_roles=True),
        dm_permission=False,
    )
    @app_commands.describe(reason="Reason for discharge")
    async def discharge(self, interaction: discord.Interaction, reason: str):
        if not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("This command can only be used by server members.", ephemeral=True)

        if not has_any_role_ids(interaction.user, ROLE_CONFIG["DISCHARGE_ALLOWED_ROLES"]):
            return await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

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
                    app_cmd.default_member_permissions = Permissions(manage_roles=True)
                except Exception:
                    pass
                try:
                    app_cmd.dm_permission = False
                except Exception:
                    pass
    except Exception:
        pass