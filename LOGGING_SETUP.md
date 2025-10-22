# NZDF Bot Logging System Setup Guide

## Overview
The logging system tracks all command usage and errors, providing comprehensive monitoring for your NZDF Discord bot.

## Features
✅ **Command Usage Logging**: Every successful slash command execution is logged with:
- User who ran the command
- Command name and parameters
- Guild and channel information
- Timestamp with user avatar

✅ **Error Logging with Admin Alerts**: When commands fail:
- Detailed error information with traceback
- Automatic ping to all bot admins
- Error categorization and debugging info
- Professional embed formatting

✅ **Admin Management Commands**: 
- `/logstatus` - Check current system status
- `/setlogchannel` - Get config help for current channel  
- `/testlog` - Test the logging system

## Quick Setup

### Step 1: Configure Logging Channel
1. Create a dedicated logging channel in your Discord server (e.g., #bot-logs)
2. Get the channel ID (Right-click channel → Copy Channel ID)
3. Update `config.py`:

```python
CHANNEL_CONFIG: ChannelConfig = {
    "CASELOG_CHANNEL": 1430467047216644196,
    "SESSION_STATUS_CHANNEL": 1427869495619354686,
    "COMMAND_LOG_CHANNEL": YOUR_CHANNEL_ID_HERE  # ← Replace with your channel ID
}
```

### Step 2: Restart Bot
Restart your bot to load the new configuration.

### Step 3: Test System
1. Run `/logstatus` to verify configuration
2. Run `/testlog` to send test logs
3. Check your logging channel for the test messages

## What Gets Logged

### Successful Commands
- ✅ Command name and user
- 📍 Server and channel location
- 🕐 Execution timestamp
- 👤 User avatar thumbnail

### Command Errors
- 🚨 Critical error alert with admin ping
- 📝 Full error details and traceback
- 👤 User who triggered the error
- 📍 Location where error occurred
- 🔍 Command that failed

### Example Log Messages
The system creates professional embeds with:
- Color coding (green for success, red for errors)
- NZDF branding and logos
- Clean formatting for easy reading
- All relevant context information

## Admin Benefits
- **Monitoring**: See all command usage patterns
- **Debugging**: Detailed error information for troubleshooting
- **Security**: Track who is using what commands
- **Maintenance**: Get notified immediately when errors occur

## Security Notes
- Only bot admins can use logging management commands
- Error pings are sent to all configured bot admins
- Logging channel should have restricted permissions
- All logs include user IDs for accountability

## Troubleshooting

### Logs Not Appearing
1. Check channel ID in config.py is correct
2. Verify bot has permission to send messages in log channel
3. Run `/logstatus` to check configuration
4. Restart bot after config changes

### Admin Pings Not Working
1. Verify bot admin IDs in config.py
2. Check bot has permission to ping users
3. Ensure admins are in the same server as the log channel

### Permission Errors
1. Bot needs "Send Messages" permission in log channel
2. Bot needs "Embed Links" permission for proper formatting
3. Bot needs "Mention Everyone" permission to ping admins

---

**Note**: The logging system is automatically loaded when the bot starts. No manual activation required after configuration.