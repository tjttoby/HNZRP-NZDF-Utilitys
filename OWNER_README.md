Owner Cog — Commands & Safety

This document describes the owner-only command set implemented in `Cogs/owner.py`.
It explains what each command does, example usage, safety notes, how command visibility and masking work, and testing tips.

IMPORTANT: The owner cog contains powerful and potentially dangerous commands (eval, shell, restart, shutdown, load/unload cogs). Only add your trusted owner ID(s) to `OWNER_IDS` in `Cogs/owner.py`.

OWNER_IDS configuration
- File: `Cogs/owner.py`
- Edit the `OWNER_IDS` set at the top of the file to include your Discord user ID(s):
  OWNER_IDS: Set[int] = {123456789012345678}

Masking and privacy
- The cog logs owner activity to the project logger `NZDF.owner`.
- Command name and description are masked in logs as "[CLASSIFIED]" per design.
- For commands that accept sensitive text (DMs, eval input, shell output), the public responses avoid printing raw sensitive data; long outputs are sent as files using binary buffers (`io.BytesIO`).

Visibility in the Discord UI
- The cog attempts to reduce UI visibility for non-privileged users by setting `default_member_permissions` to require Manage Roles and `dm_permission=False` for owner-level commands in the cog's setup.
- Note: Discord's client will only hide commands per-guild or per-app command permissions when explicit application command permissions are set (via Developer Portal or the API). To make commands visible only to you in the client UI, set per-guild command permission overrides.

List of commands (syntax and notes)

- /shutdown
  - Usage: `/shutdown`
  - Description: Safe prompt. This command now requires explicit confirmation via `/shutdown_confirm confirm:true` to actually stop the bot.
  - Notes: The initial `/shutdown` warns. Use `/shutdown_confirm` with `confirm=True` to proceed.

- /shutdown_confirm
  - Usage: `/shutdown_confirm confirm:true`
  - Description: Confirm and perform shutdown. (Owner only)
  - Notes: Requires `confirm=True` to execute.

- /restart
  - Usage: `/restart` or `/restart confirm:true`
  - Description: Restarts the Python process (exec-v). Requires `confirm=True` to run.
  - Safety: If your bot is managed by a process supervisor (systemd, PM2, Docker), prefer using that for restarts.

- /reload
  - Usage: `/reload cog:<cog_path> confirm:true`
  - Description: Reloads a cog extension (e.g., `Cogs.application`). Requires `confirm=True`.
  - Notes: Uses `bot.reload_extension` where available.

- /load
  - Usage: `/load cog:<cog_path> confirm:true`
  - Description: Loads a cog extension. Requires `confirm=True`.

- /unload
  - Usage: `/unload cog:<cog_path> confirm:true`
  - Description: Unloads a cog extension. Requires `confirm=True`.

- /status
  - Usage: `/status`
  - Description: Shows high-level bot status (guilds count, users approximate, uptime if available).

- /uptime
  - Usage: `/uptime`
  - Description: Shows the bot's uptime if a `start_time` attribute is set on the bot object.

- /userinfo
  - Usage: `/userinfo user:<user>`
  - Description: Shows basic info about the supplied user (ID, bot flag, joined, roles for guild members).

- /dmowner
  - Usage: `/dmowner message:<text>`
  - Description: Sends a DM to the owner ID configured in `OWNER_IDS`. The message content is masked in logs and the bot sends "Owner message: [CLASSIFIED]" to the owner to avoid leaking content into logs.

- /commands_for
  - Usage: `/commands_for target:<user>`
  - Description: Admin inspection tool. Shows which registered app commands a target user can likely run or see. This is an approximation, not an absolute guarantee of the Discord UI.

- /eval
  - Usage: `/eval code:<python_code>`
  - Description: Evaluates Python expressions in a minimal environment (the cog provides `bot` and `discord` in the env). Long outputs are sent as files and visible content is masked.
  - Safety: Extremely dangerous. Consider running eval in a sandboxed subprocess if you share the repo or need stronger isolation.

- /shell
  - Usage: `/shell command:<shell_command>`
  - Description: Executes a shell command on the host via `asyncio.create_subprocess_shell`. Outputs/stderr are returned; long outputs are sent as files.
  - Safety: Extremely dangerous. Consider restricting allowed commands or removing this entirely in production.

Testing and running locally
- To run unit tests, add pytest to your dev environment and create tests under `tests/`.
- Example pytest install (Windows PowerShell):
```
python -m pip install -U pip
python -m pip install pytest
```