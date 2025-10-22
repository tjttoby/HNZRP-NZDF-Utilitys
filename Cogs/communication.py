from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands
from config import ROLE_CONFIG, MEDIA, has_any_role_ids, media_file

class Communication(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="vcrequest", description="Request someone to join a voice channel")
    @app_commands.describe(
        user="The user to request",
        channel="The voice channel to join",
        reason="The reason for the request"
    )
    async def vcrequest(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        channel: discord.VoiceChannel,
        reason: str
    ):
        if not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("This command can only be used by server members.", ephemeral=True)

        if not has_any_role_ids(interaction.user, ROLE_CONFIG["VC_REQUEST_ALLOWED_ROLES"]):
            return await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

        embed = discord.Embed(
            title="🔊 VC Request",
            description=(
                f"**Hello!**\n"
                f"You have been requested to join {channel.mention} for {reason}.\n"
                f"\n"
                f"Failure to comply may result in disciplinary actions.\n"
                f"\n"
                f"Requested by {interaction.user.mention}"
                f"\nIf you are not able to join, please DM the user requesting you or reply to this message. Thank you!"
            ),
            color=discord.Color.blue()
        )

        if isinstance(interaction.channel, (discord.TextChannel, discord.Thread)):
            await interaction.response.send_message(embed=embed, allowed_mentions=discord.AllowedMentions(users=True))
        else:
            await interaction.response.send_message("This command can only be used in text channels.", ephemeral=True)

    @app_commands.command(name="say", description="Make the bot say something")
    @app_commands.describe(
        message="The message to say",
        embed="Whether to send the message as an embed"
    )
    async def say(
        self,
        interaction: discord.Interaction,
        message: str,
        embed: bool = False
    ):
        if not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("This command can only be used by server members.", ephemeral=True)

        if not has_any_role_ids(interaction.user, ROLE_CONFIG["SAY_ALLOWED_ROLES"]):
            return await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

        await interaction.response.defer(ephemeral=True)

        if not isinstance(interaction.channel, (discord.TextChannel, discord.Thread)):
            await interaction.followup.send("This command can only be used in text channels.", ephemeral=True)
            return

        if embed:
            embed_msg = discord.Embed(description=message, color=discord.Color.blue())
            await interaction.channel.send(embed=embed_msg)
        else:
            await interaction.channel.send(message)

        await interaction.followup.send("Message sent!", ephemeral=True)

    @app_commands.command(name="sign", description="Send an officially signed message")
    @app_commands.describe(message="The message to sign")
    async def sign(
        self,
        interaction: discord.Interaction,
        message: str
    ):
        if not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("This command can only be used by server members.", ephemeral=True)

        if not has_any_role_ids(interaction.user, ROLE_CONFIG["SIGNED_MESSAGE_ALLOWED_ROLES"]):
            return await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

        # Defer ephemerally to avoid command usage log
        await interaction.response.defer(ephemeral=True)

        if not isinstance(interaction.channel, (discord.TextChannel, discord.Thread)):
            await interaction.followup.send("This command can only be used in text channels.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Official Signature",
            description=message,  # Just the text, no user log
            color=discord.Color.blurple()
        )
        
        # Send to channel separately to avoid usage log
        await interaction.channel.send(embed=embed)
        
        # Confirm to user ephemerally
        await interaction.followup.send("Signed message sent!", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Communication(bot))