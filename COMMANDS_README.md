NZDF Bot — Public Commands (User-facing)

This reference lists the normal (non-owner, non-admin) commands available to regular users, their brief descriptions, usage notes, and which cog implements them. It focuses on slash commands (app commands) and common prefix commands where present.

How to read this file
- Command: the slash command name
- Usage: example parameter names (slash UI will provide types)
- Who can use: rough permission or role requirement (consult `config.py` role settings)
- Cog / file: the implementation location inside `Cogs/`

---

/callsign
- Usage: /callsign
- Description: Open a modal to request a callsign. Approved via interactive approve/deny buttons.
- Who can use: members who pass configured `CALLSIGN_REQUEST` permission (see `config.py` ROLE_CONFIG)
- Cog / file: `Cogs/callsigns.py`

/application
- Usage: /application result:<Pass|Fail> user:<member> reason:<text> notes:<text>
- Description: Post a pass/fail application embed to the channel (staff command for handling applications)
- Who can use: members who pass the configured permission check (see `config.py`/ROLE_CONFIG)
- Cog / file: `Cogs/application.py`

/medalrequest
- Usage: /medalrequest medal:<choice>
- Description: Submit a medal request; creates a thread for evidence
- Who can use: members in roles allowed to request medals (see ROLE_CONFIG)
- Cog / file: `Cogs/personnel.py`

/discharge
- Usage: /discharge reason:<text>
- Description: Submit a discharge request with a confirmable view (staff confirm button)
- Who can use: members with DISCHARGE allowed roles
- Cog / file: `Cogs/personnel.py`

/vcrequest
- Usage: /vcrequest user:<member> channel:<voice> reason:<text>
- Description: Sends a notification requesting the user to join a voice channel with reason and mention
- Who can use: roles configured in ROLE_CONFIG VC request allowed list
- Cog / file: `Cogs/communication.py`

/say
- Usage: /say message:<text> embed:<bool>
- Description: Make the bot send a message or embed in the channel (for permitted roles)
- Who can use: roles configured in ROLE_CONFIG SAY_ALLOWED_ROLES
- Cog / file: `Cogs/communication.py`

/sign
- Usage: /sign message:<text>
- Description: Send an officially signed message as an embed (for permitted roles)
- Who can use: roles configured in ROLE_CONFIG SIGNED_MESSAGE_ALLOWED_ROLES
- Cog / file: `Cogs/communication.py`

/beat
- Usage: /beat user:<member>
- Description: Fun moderation-flavored command that "beats" a user with a random item
- Who can use: roles configured in ROLE_CONFIG BEAT_ALLOWED_ROLES
- Cog / file: `Cogs/moderation.py`

/inactivity
- Usage: /inactivity user:<member>
- Description: Send an inactivity notice embed to a user or channel
- Who can use: roles configured in ROLE_CONFIG INACTIVITY_ALLOWED_ROLES
- Cog / file: `Cogs/moderation.py`

/caselog
- Usage: /caselog user:<member> punishment:<text> reason:<text>
- Description: Create a case log entry in the configured case log channel and create a thread for evidence
- Who can use: roles configured in ROLE_CONFIG CASELOG_ALLOWED_ROLES
- Cog / file: `Cogs/moderation.py`

/sessionvote
- Usage: /sessionvote
- Description: Start a vote to bring a session online. Vote buttons are posted to the session channel; requires configured session roles
- Who can use: roles configured in ROLE_CONFIG SESSION_ALLOWED_ROLES
- Cog / file: `Cogs/session.py`

/sessionshutdown
- Usage: /sessionshutdown
- Description: Shut down the session (updates status channel and posts embed)
- Who can use: roles configured in ROLE_CONFIG SESSION_ALLOWED_ROLES
- Cog / file: `Cogs/session.py`

/fonline
- Usage: /fonline
- Description: Force the session online without voting (staff use)
- Who can use: roles configured in ROLE_CONFIG SESSION_ALLOWED_ROLES
- Cog / file: `Cogs/session.py`

/sessionlowping
- Usage: /sessionlowping
- Description: Send a low ping encouraging RP participation in the configured session channel
- Who can use: roles configured in ROLE_CONFIG SESSION_ALLOWED_ROLES
- Cog / file: `Cogs/session.py`

/ping (slash)
- Usage: /ping
- Description: Check the bot's latency (slash command implementation)
- Cog / file: `Cogs/Ping.py`

/ping (prefix)
- Usage: !ping or whatever the prefix is (legacy prefix command)
- Description: Same as the slash ping but as a prefix command
- Cog / file: `Cogs/Ping.py`

---

Admin or restricted commands (not included above)
- Logging admin commands (testlog, setlogchannel, logstatus) are implemented in `Cogs/logging_system.py` and are labeled [ADMIN].
- Owner-only commands are implemented in `Cogs/owner.py` and are restricted to owner IDs.

Notes on visibility and permissions
- The project uses runtime permission checks (`has_any_role_ids`, `has_permission` etc. from `config.py`) to control who can execute commands.
- Many cogs set `default_member_permissions` defensively so commands are not shown in the UI for users without Manage Roles; this is a fallback and not a complete per-owner UI hiding strategy. For precise visibility control, use per-guild application command permissions or the Developer Portal.

If you want
- I can generate a single `commands` help command that returns this README content or a short summary in-chat.
- I can generate pytest tests for a subset of these commands (permission checks and basic behavior).
- I can produce a per-guild permission applier that tries to lock these commands to certain roles or owner-only visibility (requires bot token with appropriate permissions).

---
File generated automatically from code analysis of Cogs/ on 2025-10-23.
