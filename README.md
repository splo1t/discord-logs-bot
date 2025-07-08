# 🤖 Discord Server Logger Bot

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Discord.py](https://img.shields.io/badge/discord.py-2.0+-blue.svg)](https://discordpy.readthedocs.io/en/stable/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A comprehensive Discord logging bot that tracks **all server activities** and sends them to dedicated channels with beautiful formatting and detailed information.

## ✨ Features

### 📊 Complete Activity Tracking
The bot monitors and logs every possible server activity across **6 main categories**:

| Category | Events Tracked | Channel |
|----------|----------------|---------|
| 🗣️ **Voice Logs** | Joins, leaves, moves, mutes, deafens | `#voice-logs` |
| 💬 **Message Logs** | Sent, edited, deleted messages | `#message-logs` |
| 🛠️ **Moderation Logs** | Bans, unbans, timeouts, kicks | `#moderation-logs` |
| 🎭 **Role Logs** | Role creation, updates, assignments | `#role-logs` |
| 📦 **Channel Logs** | Channel creation, deletion, updates | `#channel-logs` |
| 🚪 **Member Logs** | Server joins and leaves | `#member-logs` |

### 🔐 Security Features
- **Admin-only configuration** - Only users with Administrator permissions can configure the bot
- **Guild-specific settings** - Each server has its own configuration
- **No persistent data storage** - All data is event-driven and temporary
- **Secure token handling** - Bot token stored in `.env` file

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- A Discord application with bot permissions

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/splo1t/discord-logs-bot.git
   cd discord-logs-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your bot**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application and bot
   - Copy the bot token

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your bot token
   ```

5. **Invite bot to server**
   
   Use this permission calculator: `Administrator` permission (or minimum required permissions)
   
   **Minimum Permissions:**
   - View Channels
   - Send Messages
   - Read Message History
   - View Audit Log
   - Use Slash Commands

6. **Run the bot**
   ```bash
   python main.py
   ```

## ⚙️ Configuration

All configuration is done through **slash commands** that are restricted to administrators:

### 📍 Set Log Channels
```
/set_log_channel category:<category> channel:<#channel>
```

**Available Categories:**
- `voice` - Voice channel activities
- `message` - Message activities  
- `moderation` - Moderation actions
- `role` - Role changes
- `channel` - Channel modifications
- `member` - Join/leave events

### 👀 View Current Setup
```
/view_log_channels
```
Shows all currently configured log channels

### 🗑️ Remove Log Channel
```
/remove_log_channel category:<category>
```
Stops logging for a specific category

## 📝 Log Examples

### Voice Activity
```
🗣️ VOICE JOIN | 2024-01-15 14:30:22
👤 JohnDoe (123456789) joined voice channel General
```

### Message Activity
```
💬 MESSAGE EDIT | 2024-01-15 14:31:15
👤 JaneDoe (987654321) in #general
📝 Before: Hello wrold
📝 After: Hello world
```

### Moderation Activity
```
🛠️ MEMBER TIMED OUT | 2024-01-15 14:32:00
⏱️ BadUser (555666777) was timed out
⌛ Duration: 60 minutes
```

## 🛡️ Privacy & Security

- **No data persistence** - The bot doesn't store any user data permanently
- **Event-driven logging** - Only logs events as they happen
- **Guild isolation** - Each server's configuration is separate
- **Permission-based access** - Only administrators can configure logging

## 🎯 Best Practices

1. **Create a dedicated log category** with appropriate channels
2. **Set proper permissions** on log channels (moderator-only viewing recommended)
3. **Configure all categories** for complete server oversight
4. **Regular monitoring** of log channels for important events

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Events not logging | Check `/view_log_channels` to verify configuration |
| Permission errors | Ensure bot has necessary permissions in log channels |
| Bot not responding | Verify intents are enabled in Discord Developer Portal |
| Commands not appearing | Wait for slash command sync (up to 1 hour) |

## 📚 Documentation

### Event Coverage
- ✅ **Voice State Changes** - All voice channel activities
- ✅ **Message Events** - Complete message lifecycle
- ✅ **Member Updates** - Role changes, timeouts, profile updates
- ✅ **Server Changes** - Channel and role modifications
- ✅ **Moderation Actions** - Bans, kicks, and restrictions
- ✅ **Audit Log Integration** - Enhanced detail capture

### Technical Details
- **Language**: Python 3.8+
- **Library**: discord.py 2.0+
- **Architecture**: Event-driven with in-memory configuration
- **Performance**: Optimized for high-activity servers

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/splo1t/discord-logs-bot/issues)
- **Discord**: [Support Server](https://discord.gg/ngx6wQAPk2)

---

<div align="center">
<strong>Made with ❤️ for the Discord community</strong>
<br>
<sub>If this project helped you, please consider giving it a ⭐!</sub>
</div>
