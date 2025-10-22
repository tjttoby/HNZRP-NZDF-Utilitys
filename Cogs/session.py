from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
from typing import Optional, Set
from config import ROLE_CONFIG, CHANNEL_CONFIG, has_any_role_ids

class SessionVoteView(View):
    def __init__(self, cog: "Session"):
        super().__init__(timeout=None)
        self.cog = cog
        self.votes: Set[int] = set()
        self.required_votes = 3

    async def update_embed(self, interaction: discord.Interaction):
        if not interaction.message:
            return

        embed = interaction.message.embeds[0]
        embed.set_field_at(0, name="Votes", value=f"`{len(self.votes)}/{self.required_votes}`")
        await interaction.message.edit(embed=embed)

        # Check if we have enough votes
        if len(self.votes) >= self.required_votes:
            # Get the session status channel
            if not interaction.guild:
                return
            
            channel = interaction.guild.get_channel(CHANNEL_CONFIG["SESSION_STATUS_CHANNEL"])
            if not isinstance(channel, discord.TextChannel):
                return

            # Delete the vote message
            await interaction.message.delete()

            # Send online message
            role = interaction.guild.get_role(ROLE_CONFIG["PING_ROLE_SESSION"])
            mention = role.mention if role else ""
            
            online_embed = discord.Embed(
                title="Session Online",
                description="The session is now online!",
                color=discord.Color.green()
            )
            
            # Create non-pressable button view
            button_view = View(timeout=None)
            button = Button(
                label="Started by Vote",
                style=discord.ButtonStyle.secondary,
                disabled=True
            )
            button_view.add_item(button)
            
            await channel.send(content=mention, embed=online_embed, view=button_view)
            
            # Update channel name
            await channel.edit(name="「🟢」nzdf-status")

    @discord.ui.button(label="Vote", style=discord.ButtonStyle.primary)
    async def vote(self, interaction: discord.Interaction, button: Button):
        if not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("Only server members can vote.", ephemeral=True)

        if not has_any_role_ids(interaction.user, ROLE_CONFIG["SESSION_ALLOWED_ROLES"]):
            return await interaction.response.send_message("You don't have permission to vote.", ephemeral=True)

        if interaction.user.id in self.votes:
            self.votes.remove(interaction.user.id)
            await interaction.response.send_message("Vote removed!", ephemeral=True)
        else:
            self.votes.add(interaction.user.id)
            await interaction.response.send_message("Vote counted!", ephemeral=True)

        await self.update_embed(interaction)

class Session(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="sessionvote", description="Start a session vote")
    async def sessionvote(self, interaction: discord.Interaction):
        if not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("This command can only be used by server members.", ephemeral=True)

        if not has_any_role_ids(interaction.user, ROLE_CONFIG["SESSION_ALLOWED_ROLES"]):
            return await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

        if not interaction.guild:
            return await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)

        # Get session channel - ALWAYS send vote here regardless of where command was used
        session_channel = interaction.guild.get_channel(CHANNEL_CONFIG["SESSION_STATUS_CHANNEL"])
        if not isinstance(session_channel, discord.TextChannel):
            return await interaction.response.send_message("Session status channel not found.", ephemeral=True)

        # Respond ephemerally first
        await interaction.response.defer(ephemeral=True)

        # Update channel name
        await session_channel.edit(name="「🟡」nzdf-status")

        # Create vote embed
        embed = discord.Embed(
            title="Session Vote",
            description="Vote to start a NZDF session!",
            color=discord.Color.dark_green()
        )
        embed.add_field(name="Votes", value="`0/3`")
        embed.set_footer(
            text=f"Vote started by: {interaction.user.display_name}!",
            icon_url=interaction.user.display_avatar.url
        )

        # Get role to ping
        role = interaction.guild.get_role(ROLE_CONFIG["PING_ROLE_SESSION"])
        mention = role.mention if role else ""

        view = SessionVoteView(self)
        # ALWAYS send to session channel, not where command was used
        await session_channel.send(content=mention, embed=embed, view=view)
        
        # Confirm to user
        await interaction.followup.send("Session vote started in the session channel!", ephemeral=True)

    @app_commands.command(name="sessionshutdown", description="Shut down the session")
    async def sessionshutdown(self, interaction: discord.Interaction):
        if not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("This command can only be used by server members.", ephemeral=True)

        if not has_any_role_ids(interaction.user, ROLE_CONFIG["SESSION_ALLOWED_ROLES"]):
            return await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

        if not interaction.guild:
            return await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)

        # Defer ephemerally first to remove command log
        await interaction.response.defer(ephemeral=True)

        # Get channel
        channel = interaction.guild.get_channel(CHANNEL_CONFIG["SESSION_STATUS_CHANNEL"])
        if not isinstance(channel, discord.TextChannel):
            return await interaction.followup.send("Session status channel not found.", ephemeral=True)

        # Update channel name
        await channel.edit(name="「⚫」nzdf-status")

        # Send shutdown message
        embed = discord.Embed(
            title="Session Offline",
            description="The session has been shut down. \n Come back next time for a NZDF session!",
            color=discord.Color.dark_grey()
        )
        
        # Create non-pressable button view
        button_view = View(timeout=None)
        button = Button(
            label=f"Shut down by: {interaction.user.display_name}",
            style=discord.ButtonStyle.secondary,
            disabled=True
        )
        button_view.add_item(button)

        await channel.send(embed=embed, view=button_view)
        await interaction.followup.send("Session shut down!", ephemeral=True)

        # Delete the last online message if it exists
        try:
            async for message in channel.history(limit=1):
                if message.embeds and message.embeds[0].title == "Session Online":
                    await message.delete()
        except discord.HTTPException:
            pass

    @app_commands.command(name="fonline", description="Force the session online without voting")
    async def fonline(self, interaction: discord.Interaction):
        if not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("This command can only be used by server members.", ephemeral=True)

        if not has_any_role_ids(interaction.user, ROLE_CONFIG["SESSION_ALLOWED_ROLES"]):
            return await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

        if not interaction.guild:
            return await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)

        # Defer ephemerally first to remove command log
        await interaction.response.defer(ephemeral=True)

        # Get the session status channel
        channel = interaction.guild.get_channel(CHANNEL_CONFIG["SESSION_STATUS_CHANNEL"])
        if not isinstance(channel, discord.TextChannel):
            return await interaction.followup.send("Session status channel not found.", ephemeral=True)

        # Update channel name to online
        await channel.edit(name="「🟢」nzdf-status")

        # Get role to ping
        role = interaction.guild.get_role(ROLE_CONFIG["PING_ROLE_SESSION"])
        mention = role.mention if role else ""

        # Send online message
        online_embed = discord.Embed(
            title="Session Online",
            description="The session has been **forced online** by staff!",
            color=discord.Color.green()
        )
        
        # Create non-pressable button view
        button_view = View(timeout=None)
        button = Button(
            label=f"Forced online by: {interaction.user.display_name}",
            style=discord.ButtonStyle.secondary,
            disabled=True
        )
        button_view.add_item(button)

        await channel.send(content=mention, embed=online_embed, view=button_view)
        await interaction.followup.send("Session forced online!", ephemeral=True)

    @app_commands.command(name="sessionlowping", description="Send a low ping encouraging RP participation")
    async def sessionlowping(self, interaction: discord.Interaction):
        if not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("This command can only be used by server members.", ephemeral=True)

        if not has_any_role_ids(interaction.user, ROLE_CONFIG["SESSION_ALLOWED_ROLES"]):
            return await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

        if not interaction.guild:
            return await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)

        # Get the session status channel
        session_channel = interaction.guild.get_channel(CHANNEL_CONFIG["SESSION_STATUS_CHANNEL"])
        if not isinstance(session_channel, discord.TextChannel):
            return await interaction.response.send_message("Session status channel not found.", ephemeral=True)

        # Defer ephemerally first
        await interaction.response.defer(ephemeral=True)

        # Get role to ping
        role = interaction.guild.get_role(ROLE_CONFIG["PING_ROLE_SESSION"])
        mention = role.mention if role else ""

        # Create low ping embed
        embed = discord.Embed(
            title="🎮 Join Us In-Game!",
            description="Hey everyone! We're looking for more people to hop in-game for some fun roleplay.\n\n**Come join us for:**\n• Engaging military roleplay\n• Training exercises\n• Operations and missions\n• Great community interaction\n\nDon't miss out on the action! 🚁",
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Sent by {interaction.user.display_name}")

        # Send to session channel
        await session_channel.send(content=mention, embed=embed)
        
        # Confirm to user
        await interaction.followup.send("Low ping sent to encourage RP participation!", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Session(bot))