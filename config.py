from __future__ import annotations
import logging
import discord
from discord import app_commands
from discord.ext import commands
from typing import Final, TypedDict
import os

# ========== CONFIG ==========

class RoleConfig(TypedDict):
    # Required role configurations
    APPLICATION_ALLOWED_ROLES: list[int]
    CALLSIGN_REQUEST_ALLOWED_ROLES: list[int]
    CALLSIGN_APPROVER_ROLES: list[int]
    BEAT_ALLOWED_ROLES: list[int]
    INACTIVITY_ALLOWED_ROLES: list[int]
    VC_REQUEST_ALLOWED_ROLES: list[int]
    CASELOG_ALLOWED_ROLES: list[int]
    MEDAL_REQUEST_ALLOWED_ROLES: list[int]
    SAY_ALLOWED_ROLES: list[int]
    DISCHARGE_ALLOWED_ROLES: list[int]
    SIGNED_MESSAGE_ALLOWED_ROLES: list[int]
    SESSION_ALLOWED_ROLES: list[int]
    PING_ALLOWED_ROLES: list[int]
    WELCOME_ALLOWED_ROLES: list[int]
    EXCLUDED_RANK_ROLES: list[int]
    PRESERVE_ROLES_ON_DISCHARGE: list[int]
    ADD_ROLES_ON_DISCHARGE: list[int]
    PING_ROLE_CALLSIGN: int
    PING_ROLE_SESSION: int

class ChannelConfig(TypedDict):
    CASELOG_CHANNEL: int
    SESSION_STATUS_CHANNEL: int
    COMMAND_LOG_CHANNEL: int

# Optional: lock slash command sync to a specific guild for testing
GUILD_ID: int | None = None

# Media paths - Easy to update for different servers
MEDIA = {
    "LOGO": "https://imgpx.com/en/1Oiy7jFITJwX.png",
    "DR": "https://imgpx.com/en/qYaMSaYGJJRZ.png",
    "FAIL": "https://imgpx.com/en/kti7BsHNEGcr.png",
    "INFRACTION": "https://imgpx.com/en/JI5jWMcgC1OH.png",
    "PASS": "https://imgpx.com/en/S3qtngsXzGW5.png",
    "PROMOTION": "https://imgpx.com/en/xPlv8Wp62Yy6.png",
    "TRAINING": "https://imgpx.com/en/5Rb1FgTvrcD3.png"
}

def media_file(key: str) -> tuple[discord.File | None, str | None]:
    """Return a File and attachment URL for a MEDIA key if the file exists.
    Example -> (discord.File(...), 'attachment://filename.png')
    """
    path = MEDIA.get(key)
    if not path:
        return None, None
    try:
        if not os.path.isfile(path):
            print(f"[MEDIA] File not found for key '{key}': {path}")
            return None, None
        filename = os.path.basename(path)
        return discord.File(path, filename=filename), f"attachment://{filename}"
    except Exception as e:
        print(f"[MEDIA] Failed to load media for '{key}': {e}")
        return None, None

# Role configuration - Update IDs for each server
ROLE_CONFIG: RoleConfig = {
    "APPLICATION_ALLOWED_ROLES": [1427869184179568712, 222222222222222222],
    "CALLSIGN_REQUEST_ALLOWED_ROLES": [1427869184179568712],
    "CALLSIGN_APPROVER_ROLES": [1427869184179568712, 444444444444444444],
    "BEAT_ALLOWED_ROLES": [1427869184179568712],
    "INACTIVITY_ALLOWED_ROLES": [1427869184179568712],
    "VC_REQUEST_ALLOWED_ROLES": [1427869184179568712],
    "CASELOG_ALLOWED_ROLES": [1427869184179568712],
    "MEDAL_REQUEST_ALLOWED_ROLES": [1427869184179568712],
    "SAY_ALLOWED_ROLES": [1427869184179568712],
    "DISCHARGE_ALLOWED_ROLES": [1427869184179568712],
    "SIGNED_MESSAGE_ALLOWED_ROLES": [1427869184179568712],
    "SESSION_ALLOWED_ROLES": [1427869184179568712],
    "PING_ALLOWED_ROLES": [1427869184179568712],
    "WELCOME_ALLOWED_ROLES": [1427869184179568712],
    "EXCLUDED_RANK_ROLES": [1427869184179568712, 666666666666666666],
    "PRESERVE_ROLES_ON_DISCHARGE": [1427869184179568712],
    "ADD_ROLES_ON_DISCHARGE": [1427869184179568712],
    "PING_ROLE_CALLSIGN": 1427869184179568712,
    "PING_ROLE_SESSION": 1427869184179568712
}

# Channel configuration - Update IDs for each server
CHANNEL_CONFIG: ChannelConfig = {
    "CASELOG_CHANNEL": 1430467047216644196,
    "SESSION_STATUS_CHANNEL": 1427869495619354686,
    "COMMAND_LOG_CHANNEL": 1430728771379531786  # Update this to your logging channel ID
}

# Medal request configuration
MEDAL_REQUEST_PING_USER: int | None = 1039388557585944656

# Bot administrators
BOT_ADMINS: Final[list[int]] = [1039388557585944656]

# Beat command items
BEAT_ITEMS: Final = [
    "A stale ANZAC biscuit of discipline",
    "A jandal blessed by the Chief of Defence",
    "A rolled-up copy of the NZDF Code of Conduct",
    "A half-eaten meat pie from the base canteen",
    "A Warrant Officer's coffee mug (filled with disappointment)",
    "A gumboot loaded with mana",
    "A cold L&P bottle (issued as non-lethal weapon)",
    "A sausage from a fundraising BBQ",
    "A laminated PowerPoint briefing",
    "A clipboard of \"urgent\" tasks",
    "A cone from the PT course obstacle line",
    "A soggy field ration (Menu 3: Chicken Curry, RIP)",
    "A beret that's seen things",
    "A pack of expired camo face paint",
    "A laminated \"Leave Denied\" form",
    "A map from the last training exercise — upside down",
    "A wet towel from the barracks shower block",
    "A 10kg sandbag of emotional damage",
    "A roll of 100-mph tape (the true fix-all weapon)",
    "A recruit's boot polish tin (still sealed)",
    "A framed photo of the Colonel's Land Rover",
    "A safety briefing that never ends",
    "A thermos of lukewarm ration tea",
    "A shovel of \"character building\"",
    "A glowing cone of reflective vengeance",
    "A camo-pattern pool noodle (tactical bonk stick)",
    "A giant kiwi bird plush (classified ordnance)",
    "A jar of Marmite",
    "A pack of TimTams — thrown for maximum morale loss",
    "A tactical jandal strike, delivered at Mach 2"
]

# Available medals
AVAILABLE_MEDALS: Final = [
    "Defence Service Medal",
    "New Zealand Defence Meritorius Service Medal",
    "New Zealand Operational Service Medal",
    "New Zealand Armed Forces Award",
    "Cadet Forces Medal",
    "New Zealand Army Long Service and Good Conduct Medal",
    "Chief of Army Commendation",
    "Chief of Defence Force Commendation",
    "New Zealand Defence Force Commendation",
    "NZSAS Wings"
]

# Command-specific user allowlists
ALLOWED_USERS: dict[str, list[int]] = {
    "PING": [1427869184179568712],
    "APPLICATION": [1427869184179568712],
    "CALLSIGN_REQUEST": [1427869184179568712],
    "CALLSIGN_APPROVE": [1427869184179568712],
    "BEAT": [1427869184179568712],
    "INACTIVITY": [1427869184179568712],
    "VC_REQUEST": [1427869184179568712],
    "CASELOG": [1427869184179568712],
    "MEDAL_REQUEST": [1427869184179568712],
    "SAY": [1427869184179568712],
    "DISCHARGE": [1427869184179568712],
    "SIGNED_MESSAGE": [1427869184179568712],
    "SESSION": [1427869184179568712],
    "WELCOME": [1427869184179568712]
}

def has_any_role_ids(member: discord.Member, role_ids: list[int]) -> bool:
    """Check if a member has any of the given role IDs."""
    if not isinstance(member, discord.Member):
        return False
    return any(role.id in role_ids for role in member.roles)

def get_highest_role(member: discord.Member) -> discord.Role | None:
    """Get the highest role of a member, excluding roles in EXCLUDED_RANK_ROLES."""
    if not isinstance(member, discord.Member):
        return None
    
    roles = [
        role for role in member.roles 
        if role.id not in ROLE_CONFIG.get("EXCLUDED_RANK_ROLES", [])
        and role.id != member.guild.id
    ]
    return max(roles, key=lambda r: r.position) if roles else None

class PermissionError(Exception):
    pass

def get_command_roles(command_name: str) -> list[int]:
    """Get the roles allowed to use a command."""
    role_map = {
        "application": ROLE_CONFIG["APPLICATION_ALLOWED_ROLES"],
        "callsign": ROLE_CONFIG["CALLSIGN_REQUEST_ALLOWED_ROLES"],
        "beat": ROLE_CONFIG["BEAT_ALLOWED_ROLES"],
        "inactivity": ROLE_CONFIG["INACTIVITY_ALLOWED_ROLES"],
        "vcrequest": ROLE_CONFIG["VC_REQUEST_ALLOWED_ROLES"],
        "caselog": ROLE_CONFIG["CASELOG_ALLOWED_ROLES"],
        "medal": ROLE_CONFIG["MEDAL_REQUEST_ALLOWED_ROLES"],
        "say": ROLE_CONFIG["SAY_ALLOWED_ROLES"],
        "discharge": ROLE_CONFIG["DISCHARGE_ALLOWED_ROLES"],
        "signed": ROLE_CONFIG["SIGNED_MESSAGE_ALLOWED_ROLES"],
        "session": ROLE_CONFIG["SESSION_ALLOWED_ROLES"],
        "ping": ROLE_CONFIG["PING_ALLOWED_ROLES"],
        "welcome": ROLE_CONFIG["WELCOME_ALLOWED_ROLES"],
    }
    return role_map.get(command_name.lower(), [])

def has_permission(member: discord.Member, command_name: str) -> bool:
    """Check if a member has permission to use a command through roles or direct allow list."""
    try:
        logger = logging.getLogger('NZDF.config')
        # Check bot admins first
        if member.id in BOT_ADMINS:
            return True
            
        # Check allowed users list
        if member.id in ALLOWED_USERS.get(command_name, []):
            return True

        # Normalize common command name variants to map to role lists
        normalized = command_name.lower().replace(' ', '').replace('_', '')
        # Try the explicit map first
        command_roles = get_command_roles(command_name)
        if not command_roles:
            # Attempt fallback mappings
            if normalized.startswith('callsign'):
                command_roles = ROLE_CONFIG.get('CALLSIGN_REQUEST_ALLOWED_ROLES', [])
            else:
                # Try the generic ROLE_CONFIG key convention
                role_config_key = f"{command_name.upper()}_ALLOWED_ROLES"
                command_roles = ROLE_CONFIG.get(role_config_key, [])

        if not command_roles:
            logger.warning('No roles configured for command %s', command_name)
            return False

        member_role_ids = [role.id for role in member.roles]
        has_perm = any(role_id in command_roles for role_id in member_role_ids)

        if not has_perm:
            logger.debug('Permission denied for %s (%s) on command %s', member.name, member.id, command_name)
            logger.debug('User roles: %s', member_role_ids)
            logger.debug('Required roles: %s', command_roles)

        return has_perm
    except Exception as e:
        print(f"Error checking permissions for {command_name}: {str(e)}")
        return False

def get_required_role_mentions(command_name: str, guild: discord.Guild | None) -> str | None:
    """Return human-friendly role mentions for required roles for a command, or None if not configured."""
    try:
        roles = get_command_roles(command_name)
        if not roles:
            roles = ROLE_CONFIG.get(f"{command_name.upper()}_ALLOWED_ROLES", [])
        if not roles:
            return None
        mentions = []
        for rid in roles:
            if guild:
                role = guild.get_role(rid)
                mentions.append(role.mention if role else f"`Role ID: {rid}`")
            else:
                mentions.append(f"`Role ID: {rid}`")
        return ", ".join(mentions)
    except Exception:
        return None