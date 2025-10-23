# 🎖️ NZDF Discord Bot

![NZDF Logo](https://imgpx.com/en/1Oiy7jFITJwX.png)

## Overview

**NZDF Bot** is a comprehensive Discord bot specifically designed and developed for **HNZRP's NZDF (New Zealand Defence Force) server**. This bot provides military-themed roleplay tools, session management, personnel administration, and moderation capabilities tailored for military simulation communities.

**🔧 Developed by:** [Tobytiwi](https://github.com/tjttoby)  
**🏠 Created for:** HNZRP's NZDF Server  
**📅 Last Updated:** October 2025  
**⚡ Framework:** discord.py with slash commands

---

## ✨ Key Features

### 🎮 **Session Management**
- **Democratic session voting** - Community-driven session starts
- **Session status tracking** - Real-time activity monitoring  
- **Force online capabilities** - Staff emergency activation
- **Activity boost pings** - Encourage participation during sessions

### 🎖️ **Personnel Administration**
- **Medal request system** - Award military honors with evidence tracking
- **Callsign management** - Request and approve tactical callsigns
- **Discharge processing** - Handle personnel departures
- **Application reviews** - Pass/fail recruitment processing

### 🛡️ **Military Operations**
- **Case logging** - Document disciplinary actions and incidents
- **Beat system** - Fun military-style corrections with random items
- **Inactivity notices** - Automated activity reminders
- **Voice channel requests** - Coordinate team communications

### 💬 **Communication Tools**
- **Official announcements** - Signed command messages
- **Channel broadcasts** - Staff messaging capabilities
- **Structured embeds** - Professional information display

### 📊 **Logging & Monitoring**
- **Comprehensive command logging** - Track all bot interactions
- **Error reporting** - Automated issue detection and reporting
- **Activity monitoring** - User engagement analytics

---

## 🎯 Command Categories

### **Session Commands**
Commands for managing training sessions and operations.

| Command | Description | Access Level |
|---------|-------------|--------------|
| `/sessionvote` | Start a democratic vote to begin a session | Session Staff |
| `/sessionshutdown` | Officially end the current session | Session Staff |
| `/fonline` | Force session online without voting (emergency) | Session Staff |
| `/sessionlowping` | Send activity boost to encourage participation | Session Staff |

### **Personnel Commands**
Military personnel administration and management.

| Command | Description | Access Level |
|---------|-------------|--------------|
| `/medalrequest <medal>` | Submit a request for military honors | Personnel |
| `/discharge <reason>` | Submit a discharge request | Authorized Staff |
| `/callsign` | Request a tactical callsign assignment | Personnel |
| `/application <result> <user> <reason> <notes>` | Process recruitment applications | Recruitment Staff |

### **Communication Commands**  
Official communications and announcements.

| Command | Description | Access Level |
|---------|-------------|--------------|
| `/vcrequest <user> <channel> <reason>` | Request someone join voice channel | Staff |
| `/say <message> [embed]` | Make bot send a message | Staff |
| `/sign <message>` | Send officially signed announcement | Command Staff |

### **Moderation Commands**
Military discipline and case management.

| Command | Description | Access Level |
|---------|-------------|--------------|
| `/beat <user>` | Apply fun disciplinary action with random item | Moderation Staff |
| `/inactivity <user>` | Send inactivity notice | Moderation Staff |
| `/caselog <user> <punishment> <reason>` | Create formal case log entry | Moderation Staff |

### **Utility Commands**
General bot utilities and information.

| Command | Description | Access Level |
|---------|-------------|--------------|
| `/ping` | Check bot latency and status | Everyone |

### **Admin Commands**
Bot administration and logging management.

| Command | Description | Access Level |
|---------|-------------|--------------|
| `/testlog` | Test the logging system | Bot Admins |
| `/setlogchannel` | Configure logging channel | Bot Admins |
| `/logstatus` | Check logging system status | Bot Admins |

---

## 🔧 Technical Features

### **Smart Permission System**
- **Role-based access control** - Commands automatically check user permissions
- **UI visibility management** - Users only see commands they can access
- **Hierarchical permissions** - Different access levels for different roles

### **Enhanced User Experience**
- **Rich embeds** - Professional military-themed message formatting
- **Interactive buttons** - Approval workflows and confirmations
- **Thread creation** - Organized evidence submission and discussions  
- **Dynamic timestamps** - Real-time relative time displays

### **Robust Error Handling**
- **Comprehensive logging** - All activities tracked and logged
- **Graceful degradation** - Bot continues functioning during issues
- **User-friendly errors** - Clear error messages without technical jargon

### **Military Theming**
- **NZDF branding** - Consistent visual identity throughout
- **Military terminology** - Authentic language and procedures
- **Honor system integration** - Medal and recognition workflows

---

## 🛠️ Configuration

The bot uses a centralized configuration system in `config.py` that allows server administrators to:

- **Configure role permissions** for each command category
- **Set channel destinations** for logging and operations
- **Customize medal types** and availability
- **Adjust ping roles** for notifications
- **Modify disciplinary items** for the beat system

### **Required Permissions**
The bot requires the following Discord permissions:
- **Send Messages** - Basic communication
- **Embed Links** - Rich message formatting  
- **Manage Messages** - Message management and cleanup
- **Create Public Threads** - Evidence submission workflows
- **Mention Everyone** - Role pings for notifications
- **Use Slash Commands** - Modern command interface

---

## 📋 Setup Requirements

### **Python Dependencies**
- `discord.py` (v2.0+) - Discord API interaction
- `python-dotenv` - Environment variable management
- Python 3.8+ - Modern Python features

### **Discord Setup**
1. Create bot application in Discord Developer Portal
2. Generate bot token and add to `.env` file
3. Invite bot with required permissions
4. Configure roles and channels in `config.py`

### **File Structure**
```
NZDF_Bot/
├── bot.py                 # Main bot entry point
├── config.py             # Centralized configuration
├── .env                  # Environment variables (not in repo)
├── Cogs/                 # Command modules
│   ├── session.py        # Session management
│   ├── personnel.py      # Personnel administration  
│   ├── moderation.py     # Discipline and cases
│   ├── communication.py  # Announcements and messaging
│   ├── application.py    # Recruitment processing
│   ├── callsigns.py      # Callsign management
│   ├── logging_system.py # Activity logging
│   └── Ping.py          # Utility commands
└── README.md            # This documentation
```

---

## 🎖️ About HNZRP

**HNZRP (Hardcore New Zealand Roleplay)** is a military simulation community focused on realistic New Zealand Defence Force operations and training. The server provides:

- **Authentic military roleplay** experiences
- **Structured training programs** and career progression  
- **Realistic operations** and mission scenarios
- **Professional military culture** and discipline
- **Community-driven** events and activities

This bot was specifically designed to support HNZRP's unique requirements for military-style administration, session management, and community engagement.

---

## 🔒 Security & Privacy

- **No sensitive data** stored in bot code or repository
- **Environment variables** used for all sensitive configuration
- **Permission-based access** ensures proper command restriction
- **Audit logging** tracks all administrative actions
- **Role verification** prevents unauthorized access

---

## 📞 Support & Development

**Developer:** Tobytiwi  
**GitHub:** [tjttoby](https://github.com/tjttoby)  
**Repository:** [HNZRP-NZDF-Utilitys](https://github.com/tjttoby/HNZRP-NZDF-Utilitys)

For bug reports, feature requests, or technical support, please:
1. Check existing issues on GitHub
2. Create a detailed issue report  
3. Contact the developer directly if urgent

---

## 📜 License & Usage

This bot is **custom-built exclusively for HNZRP's NZDF server**. While the code is available for reference and learning, it contains server-specific configurations and branding.

**Usage Guidelines:**
- ✅ Learning and educational reference
- ✅ Inspiration for similar projects
- ❌ Direct deployment without modification
- ❌ Commercial use without permission

---

## 🎯 Version History

**v2.0** (October 2025)
- Complete rewrite with modern discord.py
- Enhanced embed designs and user experience  
- Improved error handling and logging
- Added interactive button workflows
- Military-themed visual improvements

**v1.0** (Initial Release)
- Basic command functionality
- Core session management
- Personnel administration tools

---

**⚡ Built with precision. Deployed with pride. Serving the NZDF community.**
