from __future__ import annotations

import discord
from discord import app_commands, Permissions
from discord.ext import commands
from discord.ui import Modal, TextInput, Button, View
from typing import Optional
import asyncio
import time
import logging
from config import ROLE_CONFIG, MEDIA, get_highest_role, has_permission, media_file

logger = logging.getLogger('NZDF.callsigns')
MANAGER_ROLE_ID = 1427869184179568712

class CallsignModal(Modal, title="Callsign Request"):
    callsign = TextInput(
        label="Requested Callsign",
        placeholder="Enter your desired callsign...",
        min_length=2,
        max_length=32,
    )

    def __init__(self, cog: Callsigns):
        super().__init__()
        self.cog = cog

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message("This command can only be used by server members.", ephemeral=True)
            return None

        highest_role = get_highest_role(interaction.user)
        if not highest_role:
            await interaction.response.send_message("Could not determine your rank.", ephemeral=True)
            return None

        embed = discord.Embed(
            title="🏷️ Callsign Authorization Request",
            description=f"**Personnel Callsign Assignment Request**\n\nA member has requested a new tactical callsign for operational use.",
            color=discord.Color.orange()
        )
        embed.add_field(
            name="🎯 Requested Callsign", 
            value=f"**{self.callsign.value}**",
            inline=False
        )
        embed.add_field(
            name="👤 Requesting Member", 
            value=f"{interaction.user.mention}\n*{interaction.user.display_name}*",
            inline=True
        )
        embed.add_field(
            name="🎖️ Current Rank", 
            value=f"**{highest_role.name}**",
            inline=True
        )
        embed.add_field(
            name="📅 Request Time", 
            value=f"<t:{int(discord.utils.utcnow().timestamp())}:R>",
            inline=True
        )
        embed.add_field(
            name="⚡ Action Required", 
            value="**Command approval needed**\n• Review callsign appropriateness\n• Verify member eligibility\n• Approve or deny request",
            inline=False
        )
        embed.set_thumbnail(url=MEDIA.get("LOGO", ""))
        embed.set_footer(
            text="Callsign requests require command authorization • Use buttons below to approve/deny",
            icon_url=interaction.user.display_avatar.url
        )
        files = []

        # Create approval buttons
        view = CallsignApprovalView(self.cog, interaction.user, self.callsign.value)
        
        # Send the request with mention above (no usage log)
        if interaction.channel and isinstance(interaction.channel, (discord.TextChannel, discord.Thread)):
            role = interaction.guild.get_role(ROLE_CONFIG["PING_ROLE_CALLSIGN"]) if interaction.guild else None
            mention = role.mention if role else ""
            await interaction.response.send_message("Request submitted!", ephemeral=True)
            await interaction.channel.send(content=mention, embed=embed, view=view)
        else:
            await interaction.response.send_message("This command can only be used in text channels.", ephemeral=True)

class CallsignApprovalView(View):
    def __init__(self, cog: Callsigns, requestor: discord.Member, callsign: str):
        super().__init__(timeout=None)
        self.cog = cog
        self.requestor = requestor
        self.callsign = callsign
        self.approved = None
        self.switch_count = 0
        self.max_switches = 4
        self.creation_time = time.time()
        self.timeout_hours = 5

    def _check_timeout(self) -> bool:
        """Check if 5 hours have passed since creation"""
        return (time.time() - self.creation_time) > (self.timeout_hours * 3600)

    def _update_buttons(self):
        """Update button states based on current status and switch count"""
        if self._check_timeout() or self.switch_count >= self.max_switches:
            # Disable both buttons
            for item in self.children:
                if isinstance(item, Button):
                    item.disabled = True
        else:
            # Enable/disable based on current state
            for item in self.children:
                if isinstance(item, Button):
                    if item.custom_id == "approve_callsign":
                        item.disabled = (self.approved == True)
                        item.style = discord.ButtonStyle.secondary if self.approved == True else discord.ButtonStyle.green
                    elif item.custom_id == "deny_callsign":
                        item.disabled = (self.approved == False)
                        item.style = discord.ButtonStyle.secondary if self.approved == False else discord.ButtonStyle.red

    async def _send_dm(self, status: str):
        """Send DM to requestor with embed"""
        try:
            embed = discord.Embed(
                title="🏷️ Callsign Request Update",
                description=f"Your callsign **{self.callsign}** was **{status}**.\n\nPlease change your nickname (if it has not been done for you).",
                color=discord.Color.green() if status == "accepted" else discord.Color.red()
            )
            embed.set_thumbnail(url=MEDIA["LOGO"])
            await self.requestor.send(embed=embed)
        except discord.HTTPException:
            pass  # User might have DMs disabled

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green, custom_id="approve_callsign")
    async def approve(self, interaction: discord.Interaction, button: Button):
        if not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("This action can only be performed by server members.", ephemeral=True)

        # Require manager role to approve
        if not any(getattr(r, 'id', None) == MANAGER_ROLE_ID for r in interaction.user.roles):
            logger.debug('User %s attempted to approve without manager role', getattr(interaction.user, 'id', None))
            role_obj = interaction.guild.get_role(MANAGER_ROLE_ID) if interaction.guild else None
            mention_text = role_obj.mention if role_obj else f"`Role ID: {MANAGER_ROLE_ID}`"
            return await interaction.response.send_message(f"You don't have permission to approve callsigns. Required role: {mention_text}", ephemeral=True)

        if self._check_timeout():
            return await interaction.response.send_message("This request has timed out after 5 hours.", ephemeral=True)

        if self.switch_count >= self.max_switches:
            return await interaction.response.send_message("Maximum number of status changes reached.", ephemeral=True)

        # Update status
        old_status = self.approved
        self.approved = True
        if old_status != True:
            self.switch_count += 1

        if not interaction.message or not interaction.message.embeds:
            await interaction.response.send_message("Could not find the original message.", ephemeral=True)
            return

        embed = interaction.message.embeds[0].copy()
        embed.color = discord.Color.green()
        
        # Update or add status field
        status_field_index = None
        for i, field in enumerate(embed.fields):
            if field.name == "Status":
                status_field_index = i
                break
        
        status_text = f"✅ Approved by {interaction.user.mention}"
        if self.switch_count > 0:
            status_text += f" (Changes: {self.switch_count}/{self.max_switches})"
            
        if status_field_index is not None:
            embed.set_field_at(status_field_index, name="Status", value=status_text, inline=False)
        else:
            embed.add_field(name="Status", value=status_text, inline=False)

        # Update buttons
        self._update_buttons()

        await interaction.message.edit(embed=embed, view=self)
        
        # Send DM
        await self._send_dm("accepted")

        await interaction.response.send_message("Callsign request approved!", ephemeral=True)

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red, custom_id="deny_callsign")
    async def deny(self, interaction: discord.Interaction, button: Button):
        if not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("This action can only be performed by server members.", ephemeral=True)

        # Require manager role to deny
        if not any(getattr(r, 'id', None) == MANAGER_ROLE_ID for r in interaction.user.roles):
            logger.debug('User %s attempted to deny without manager role', getattr(interaction.user, 'id', None))
            role_obj = interaction.guild.get_role(MANAGER_ROLE_ID) if interaction.guild else None
            mention_text = role_obj.mention if role_obj else f"`Role ID: {MANAGER_ROLE_ID}`"
            return await interaction.response.send_message(f"You don't have permission to deny callsigns. Required role: {mention_text}", ephemeral=True)

        if self._check_timeout():
            return await interaction.response.send_message("This request has timed out after 5 hours.", ephemeral=True)

        if self.switch_count >= self.max_switches:
            return await interaction.response.send_message("Maximum number of status changes reached.", ephemeral=True)

        # Update status
        old_status = self.approved
        self.approved = False
        if old_status != False:
            self.switch_count += 1

        if not interaction.message or not interaction.message.embeds:
            await interaction.response.send_message("Could not find the original message.", ephemeral=True)
            return

        embed = interaction.message.embeds[0].copy()
        embed.color = discord.Color.red()
        
        # Update or add status field
        status_field_index = None
        for i, field in enumerate(embed.fields):
            if field.name == "Status":
                status_field_index = i
                break
        
        status_text = f"❌ Denied by {interaction.user.mention}"
        if self.switch_count > 0:
            status_text += f" (Changes: {self.switch_count}/{self.max_switches})"
            
        if status_field_index is not None:
            embed.set_field_at(status_field_index, name="Status", value=status_text, inline=False)
        else:
            embed.add_field(name="Status", value=status_text, inline=False)

        # Update buttons
        self._update_buttons()

        await interaction.message.edit(embed=embed, view=self)
        
        # Send DM
        await self._send_dm("denied")

        await interaction.response.send_message("Callsign request denied!", ephemeral=True)

class Callsigns(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="callsign", description="Request a callsign")
    async def callsign(self, interaction: discord.Interaction):
        if not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("This command can only be used by server members.", ephemeral=True)

        # No role required to request a callsign; anyone who is a guild member may request.

        modal = CallsignModal(self)
        await interaction.response.send_modal(modal)

async def setup(bot: commands.Bot):
    cog = Callsigns(bot)
    await bot.add_cog(cog)

    # Defensive visibility attributes for slash command
    try:
        app_cmd = bot.tree.get_command('callsign')
        if app_cmd:
            # Set default_member_permissions to hide command from users without manage_roles
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