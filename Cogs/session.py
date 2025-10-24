from __future__ import annotations

import discord
from discord import app_commands, Permissions
from discord.ext import commands
from discord.ui import View, Button
from typing import Optional, Set
import config
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
        # Update vote count with better formatting
        votes_text = f"**{len(self.votes)}/{self.required_votes}** votes needed"
        if len(self.votes) >= self.required_votes:
            votes_text = f"**{len(self.votes)}/{self.required_votes}** ✅ **READY TO START!**"
        
        embed.set_field_at(0, name="📊 Current Votes", value=votes_text)
        
        # Update status field based on vote progress
        if len(self.votes) >= self.required_votes:
            embed.set_field_at(1, name="⏰ Status", value="🟢 **Starting Session...**")
            embed.color = discord.Color.green()
        elif len(self.votes) >= self.required_votes - 1:
            embed.set_field_at(1, name="⏰ Status", value="🟠 **Almost Ready!**")
            embed.color = discord.Color.orange()
        else:
            embed.set_field_at(1, name="⏰ Status", value="🟡 **Voting in Progress**")
        
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
                title="🟢 Session is Now ONLINE!",
                description="**🎉 The session has officially started!**\n\n**Join us for:**\n🚁 **Military Operations** - Coordinated missions\n🎯 **Training Exercises** - Skill development\n👥 **Team Building** - Work together\n🏆 **Achievement Hunting** - Earn recognition\n\n**Get in-game and join the action! 🎮**",
                color=discord.Color.green()
            )
            online_embed.add_field(
                name="📊 Vote Results",
                value=f"✅ **{len(self.votes)}/{self.required_votes}** votes achieved",
                inline=True
            )
            online_embed.add_field(
                name="🕐 Session Started",
                value="<t:{}:R>".format(int(discord.utils.utcnow().timestamp())),
                inline=True
            )
            online_embed.add_field(
                name="🎮 Status",
                value="🟢 **LIVE & ACTIVE**",
                inline=True
            )
            online_embed.set_thumbnail(url=config.MEDIA.get("LOGO", ""))
            online_embed.set_footer(text="Session started via democratic vote • Good luck out there!")
            
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

    @discord.ui.button(label="🗳️ Vote to Start", style=discord.ButtonStyle.primary, emoji="⚡")
    async def vote(self, interaction: discord.Interaction, button: Button):
        if not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("❌ Only server members can vote.", ephemeral=True)

        if not config.has_permission(interaction.user, "session"):
            required_roles = config.get_required_role_mentions("session", interaction.guild)
            msg = "❌ You don't have permission to vote for sessions."
            if required_roles:
                msg += f" Required roles: {required_roles}"
            return await interaction.response.send_message(msg, ephemeral=True)

        if interaction.user.id in self.votes:
            self.votes.remove(interaction.user.id)
            await interaction.response.send_message("🗳️ **Vote removed!** Changed your mind? That's okay!", ephemeral=True)
        else:
            self.votes.add(interaction.user.id)
            await interaction.response.send_message("✅ **Vote counted!** Thanks for supporting the session!", ephemeral=True)

        await self.update_embed(interaction)

class Session(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="sessionvote", description="Start a session vote")
    async def sessionvote(self, interaction: discord.Interaction):
        if not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("This command can only be used by server members.", ephemeral=True)

        if not config.has_permission(interaction.user, "session"):
            required_roles = config.get_required_role_mentions("session", interaction.guild)
            msg = "❌ You don't have permission to use this command."
            if required_roles:
                msg += f" Required roles: {required_roles}"
            return await interaction.response.send_message(msg, ephemeral=True)

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
            title="🗳️ Session Vote Started",
            description="**🎮 Ready for some NZDF action?**\n\nClick the button below to vote for starting a session!\n\n**What to expect:**\n🚁 Military Operations\n🎯 Training Exercises  \n👥 Team Coordination\n🏆 Achievement Opportunities",
            color=discord.Color.gold()
        )
        embed.add_field(
            name="📊 Current Votes", 
            value="**0/3** votes needed",
            inline=True
        )
        embed.add_field(
            name="⏰ Status", 
            value="🟡 **Voting in Progress**",
            inline=True
        )
        embed.add_field(
            name="🎯 Required", 
            value="**3** votes to start",
            inline=True
        )
        embed.set_footer(
            text=f"Vote initiated by {interaction.user.display_name} • React to participate!",
            icon_url=interaction.user.display_avatar.url
        )
        embed.set_thumbnail(url=config.MEDIA.get("LOGO", ""))

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

        if not config.has_permission(interaction.user, "session"):
            required_roles = config.get_required_role_mentions("session", interaction.guild)
            msg = "❌ You don't have permission to use this command."
            if required_roles:
                msg += f" Required roles: {required_roles}"
            return await interaction.response.send_message(msg, ephemeral=True)

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
            title="⚫ Session OFFLINE",
            description="**📴 The session has been officially shut down**\n\n**Thank you for participating!**\n\n🎖️ **Session Summary:**\n• Great teamwork and coordination\n• Mission objectives completed\n• Valuable training experience gained\n\n**Next Session:**\n🔔 Stay tuned for the next session announcement\n🗳️ Vote when the next session poll goes live\n💪 Keep practicing and stay sharp!\n\n**See you next time, soldier! 🫡**",
            color=discord.Color.dark_grey()
        )
        embed.add_field(
            name="🕐 Session Ended",
            value="<t:{}:R>".format(int(discord.utils.utcnow().timestamp())),
            inline=True
        )
        embed.add_field(
            name="👤 Shut down by",
            value=f"**{interaction.user.display_name}**",
            inline=True
        )
        embed.add_field(
            name="📊 Status",
            value="⚫ **OFFLINE**",
            inline=True
        )
        embed.set_thumbnail(url=config.MEDIA.get("LOGO", ""))
        embed.set_footer(text="Session concluded • Thanks for your service!")
        
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

        if not config.has_permission(interaction.user, "session"):
            required_roles = config.get_required_role_mentions("session", interaction.guild)
            msg = "❌ You don't have permission to use this command."
            if required_roles:
                msg += f" Required roles: {required_roles}"
            return await interaction.response.send_message(msg, ephemeral=True)

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
            title="🟢 Session FORCE STARTED!",
            description="**⚡ Emergency session activation by command staff!**\n\n**🚨 IMMEDIATE DEPLOYMENT REQUIRED**\n\n**Mission Details:**\n🎯 **High Priority Operations** - Critical missions active\n🚁 **Rapid Response** - Quick deployment needed\n👥 **All Hands on Deck** - Maximum participation required\n🏆 **Elite Performance** - Show your best skills\n\n**Get in-game NOW! This is not a drill! 🔥**",
            color=discord.Color.green()
        )
        online_embed.add_field(
            name="🕐 Force Started",
            value="<t:{}:R>".format(int(discord.utils.utcnow().timestamp())),
            inline=True
        )
        online_embed.add_field(
            name="👤 Authorized by",
            value=f"**{interaction.user.display_name}**\n*Command Staff*",
            inline=True
        )
        online_embed.add_field(
            name="🚨 Priority Level",
            value="🔴 **URGENT**",
            inline=True
        )
        online_embed.set_thumbnail(url=config.MEDIA.get("LOGO", ""))
        online_embed.set_footer(text="Emergency session • Immediate response required!")
        
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

        if not config.has_permission(interaction.user, "session"):
            required_roles = config.get_required_role_mentions("session", interaction.guild)
            msg = "❌ You don't have permission to use this command."
            if required_roles:
                msg += f" Required roles: {required_roles}"
            return await interaction.response.send_message(msg, ephemeral=True)

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
            title="🎮 Join the Action - More Players Needed!",
            description="**🌟 Hey there, soldiers!**\n\nWe've got some fantastic roleplay happening right now and we'd love more people to join the fun!\n\n**🔥 What's happening:**\n🚁 **Active Operations** - Live missions in progress\n🎯 **Training Scenarios** - Perfect for skill building  \n👥 **Team Coordination** - Work with experienced players\n🏆 **Progression Opportunities** - Advance your character\n⚡ **Dynamic Events** - Spontaneous action\n\n**🎪 Why join now:**\n• Session is already warmed up and active\n• Great community atmosphere\n• Perfect time to jump in and participate\n• Opportunities for leadership and teamwork\n\n**Ready to serve? Get in-game and join your unit! 🫡**",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="🎯 Current Activity",
            value="🟢 **ACTIVE SESSION**",
            inline=True
        )
        embed.add_field(
            name="👥 Looking for",
            value="**All Roles** 🎖️",
            inline=True
        )
        embed.add_field(
            name="⏰ Join Time",
            value="**Right Now!** ⚡",
            inline=True
        )
        embed.set_thumbnail(url=config.MEDIA.get("LOGO", ""))
        embed.set_footer(
            text=f"Activity boost by {interaction.user.display_name} • Answer the call!",
            icon_url=interaction.user.display_avatar.url
        )

        # Send to session channel
        await session_channel.send(content=mention, embed=embed)
        
        # Confirm to user
        await interaction.followup.send("Low ping sent to encourage RP participation!", ephemeral=True)

async def setup(bot: commands.Bot):
    cog = Session(bot)
    await bot.add_cog(cog)

    # Defensive visibility attributes for slash commands
    try:
        for cmd_name in ('sessionvote', 'sessionshutdown', 'fonline', 'sessionlowping'):
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