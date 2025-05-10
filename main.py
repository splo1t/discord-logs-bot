import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ServerLogger")

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Bot setup with necessary intents for comprehensive logging
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Store guild configurations in memory
# Format: {guild_id: {"voice": channel_id, "message": channel_id, ...}}
guild_configs = {}

# Log message template for consistent formatting
def format_log(event_type, content):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"**{event_type}** | `{timestamp}`\n{content}"

# Utility function to check if a log channel is configured
async def get_log_channel(guild_id, log_type):
    if guild_id not in guild_configs or log_type not in guild_configs[guild_id]:
        return None
    
    channel_id = guild_configs[guild_id][log_type]
    channel = bot.get_channel(channel_id)
    return channel

# Utility function to send log message
async def send_log(guild_id, log_type, event_type, content):
    channel = await get_log_channel(guild_id, log_type)
    if channel:
        try:
            await channel.send(format_log(event_type, content))
        except discord.HTTPException as e:
            logger.error(f"Failed to send log message: {e}")
    else:
        logger.debug(f"No log channel configured for {log_type} in guild {guild_id}")

# Check if user has administrator permissions
def is_admin(interaction: discord.Interaction):
    return interaction.user.guild_permissions.administrator

@bot.event
async def on_ready():
    logger.info(f"{bot.user.name} has connected to Discord!")
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")

# ==================== VOICE LOGS ====================
@bot.event
async def on_voice_state_update(member, before, after):
    guild_id = member.guild.id
    
    # Member joins a voice channel
    if before.channel is None and after.channel is not None:
        content = f"👤 **{member.display_name}** (`{member.id}`) joined voice channel **{after.channel.name}**"
        await send_log(guild_id, "voice", "VOICE JOIN", content)
    
    # Member leaves a voice channel
    elif before.channel is not None and after.channel is None:
        content = f"👤 **{member.display_name}** (`{member.id}`) left voice channel **{before.channel.name}**"
        await send_log(guild_id, "voice", "VOICE LEAVE", content)
    
    # Member moved between voice channels
    elif before.channel is not None and after.channel is not None and before.channel != after.channel:
        content = f"👤 **{member.display_name}** (`{member.id}`) moved from **{before.channel.name}** to **{after.channel.name}**"
        await send_log(guild_id, "voice", "VOICE MOVE", content)
    
    # Member server muted/unmuted
    if before.mute != after.mute:
        status = "muted" if after.mute else "unmuted"
        content = f"👤 **{member.display_name}** (`{member.id}`) was server {status} in **{after.channel.name}**"
        await send_log(guild_id, "voice", f"VOICE {status.upper()}", content)
    
    # Member self muted/unmuted
    if before.self_mute != after.self_mute:
        status = "self-muted" if after.self_mute else "self-unmuted"
        content = f"👤 **{member.display_name}** (`{member.id}`) {status} in **{after.channel.name}**"
        await send_log(guild_id, "voice", f"VOICE {status.upper()}", content)
    
    # Member server deafened/undeafened
    if before.deaf != after.deaf:
        status = "deafened" if after.deaf else "undeafened"
        content = f"👤 **{member.display_name}** (`{member.id}`) was server {status} in **{after.channel.name}**"
        await send_log(guild_id, "voice", f"VOICE {status.upper()}", content)
    
    # Member self deafened/undeafened
    if before.self_deaf != after.self_deaf:
        status = "self-deafened" if after.self_deaf else "self-undeafened"
        content = f"👤 **{member.display_name}** (`{member.id}`) {status} in **{after.channel.name}**"
        await send_log(guild_id, "voice", f"VOICE {status.upper()}", content)

# ==================== MESSAGE LOGS ====================
@bot.event
async def on_message(message):
    # Skip bot messages
    if message.author.bot:
        return
    
    guild_id = message.guild.id if message.guild else None
    if guild_id:
        content = (
            f"👤 **{message.author.display_name}** (`{message.author.id}`) in {message.channel.mention}\n"
            f"📝 **Content:** {message.content}"
        )
        
        # Add attachment info if any
        if message.attachments:
            attachment_links = [f"[Attachment {i+1}]({a.url})" for i, a in enumerate(message.attachments)]
            content += f"\n📎 **Attachments:** {', '.join(attachment_links)}"
            
        await send_log(guild_id, "message", "MESSAGE SENT", content)
    
    # Continue with command processing
    await bot.process_commands(message)

@bot.event
async def on_message_edit(before, after):
    # Skip bot messages
    if before.author.bot:
        return
    
    # Skip if content didn't change (embed loads, etc.)
    if before.content == after.content:
        return
        
    guild_id = before.guild.id if before.guild else None
    if guild_id:
        content = (
            f"👤 **{before.author.display_name}** (`{before.author.id}`) in {before.channel.mention}\n"
            f"📝 **Before:** {before.content}\n"
            f"📝 **After:** {after.content}"
        )
        await send_log(guild_id, "message", "MESSAGE EDIT", content)

@bot.event
async def on_message_delete(message):
    # Skip bot messages
    if message.author.bot:
        return
        
    guild_id = message.guild.id if message.guild else None
    if guild_id:
        content = (
            f"👤 **{message.author.display_name}** (`{message.author.id}`) in {message.channel.mention}\n"
            f"📝 **Deleted Content:** {message.content}"
        )
        
        # Add attachment info if any
        if message.attachments:
            attachment_links = [f"[Attachment {i+1}]({a.url})" for i, a in enumerate(message.attachments)]
            content += f"\n📎 **Attachments:** {', '.join(attachment_links)}"
            
        await send_log(guild_id, "message", "MESSAGE DELETE", content)

# ==================== MODERATION LOGS ====================
@bot.event
async def on_member_ban(guild, user):
    content = f"🔨 **{user.name}** (`{user.id}`) was banned from the server"
    await send_log(guild.id, "moderation", "MEMBER BANNED", content)

@bot.event
async def on_member_unban(guild, user):
    content = f"🔓 **{user.name}** (`{user.id}`) was unbanned from the server"
    await send_log(guild.id, "moderation", "MEMBER UNBANNED", content)

# Timeout events require audit log checking
@bot.event
async def on_member_update(before, after):
    guild_id = before.guild.id
    
    # Check for timeout (communication_disabled_until)
    if before.timed_out_until != after.timed_out_until:
        if after.timed_out_until is not None:
            # Member was timed out
            timeout_duration = after.timed_out_until - datetime.now().astimezone()
            content = (
                f"⏱️ **{after.display_name}** (`{after.id}`) was timed out\n"
                f"⌛ **Duration:** {timeout_duration.total_seconds() // 60} minutes"
            )
            await send_log(guild_id, "moderation", "MEMBER TIMED OUT", content)
        else:
            # Member timeout was removed
            content = f"⏱️ **{after.display_name}** (`{after.id}`) had their timeout removed"
            await send_log(guild_id, "moderation", "TIMEOUT REMOVED", content)

# ==================== ROLE LOGS ====================
@bot.event
async def on_guild_role_create(role):
    guild_id = role.guild.id
    content = f"🎭 Role **{role.name}** (`{role.id}`) was created"
    await send_log(guild_id, "role", "ROLE CREATED", content)

@bot.event
async def on_guild_role_delete(role):
    guild_id = role.guild.id
    content = f"🎭 Role **{role.name}** (`{role.id}`) was deleted"
    await send_log(guild_id, "role", "ROLE DELETED", content)

@bot.event
async def on_guild_role_update(before, after):
    guild_id = before.guild.id
    
    # Only log if something relevant changed
    changes = []
    
    if before.name != after.name:
        changes.append(f"**Name:** '{before.name}' → '{after.name}'")
    
    if before.color != after.color:
        changes.append(f"**Color:** {before.color} → {after.color}")
    
    if before.permissions != after.permissions:
        # Get the permission changes
        added_perms = [p[0] for p in after.permissions if p not in before.permissions and p[1]]
        removed_perms = [p[0] for p in before.permissions if p not in after.permissions and p[1]]
        
        if added_perms:
            changes.append(f"**Added Permissions:** {', '.join(added_perms)}")
        if removed_perms:
            changes.append(f"**Removed Permissions:** {', '.join(removed_perms)}")
    
    if changes:
        content = f"🎭 Role **{after.name}** (`{after.id}`) was updated\n" + "\n".join(changes)
        await send_log(guild_id, "role", "ROLE UPDATED", content)

@bot.event
async def on_member_update(before, after):
    guild_id = before.guild.id
    
    # Check for role changes
    added_roles = [role for role in after.roles if role not in before.roles]
    removed_roles = [role for role in before.roles if role not in after.roles]
    
    if added_roles:
        roles_text = ", ".join([f"**{role.name}**" for role in added_roles])
        content = f"👤 **{after.display_name}** (`{after.id}`) was given the following role(s): {roles_text}"
        await send_log(guild_id, "role", "ROLES ADDED", content)
    
    if removed_roles:
        roles_text = ", ".join([f"**{role.name}**" for role in removed_roles])
        content = f"👤 **{after.display_name}** (`{after.id}`) had the following role(s) removed: {roles_text}"
        await send_log(guild_id, "role", "ROLES REMOVED", content)

# ==================== CHANNEL LOGS ====================
@bot.event
async def on_guild_channel_create(channel):
    guild_id = channel.guild.id
    content = f"📁 Channel **{channel.name}** (`{channel.id}`) was created\n**Type:** {channel.type}"
    await send_log(guild_id, "channel", "CHANNEL CREATED", content)

@bot.event
async def on_guild_channel_delete(channel):
    guild_id = channel.guild.id
    content = f"🗑️ Channel **{channel.name}** (`{channel.id}`) was deleted\n**Type:** {channel.type}"
    await send_log(guild_id, "channel", "CHANNEL DELETED", content)

@bot.event
async def on_guild_channel_update(before, after):
    guild_id = before.guild.id
    
    # Only log if something relevant changed
    changes = []
    
    if before.name != after.name:
        changes.append(f"**Name:** '{before.name}' → '{after.name}'")
    
    # For text channels, check topic
    if hasattr(before, 'topic') and hasattr(after, 'topic') and before.topic != after.topic:
        before_topic = before.topic if before.topic else "(none)"
        after_topic = after.topic if after.topic else "(none)"
        changes.append(f"**Topic:** '{before_topic}' → '{after_topic}'")
    
    # Channel type (if applicable)
    if before.type != after.type:
        changes.append(f"**Type:** {before.type} → {after.type}")
    
    if changes:
        content = f"📁 Channel **{after.name}** (`{after.id}`) was updated\n" + "\n".join(changes)
        await send_log(guild_id, "channel", "CHANNEL UPDATED", content)

# ==================== JOIN/LEAVE LOGS ====================
@bot.event
async def on_member_join(member):
    guild_id = member.guild.id
    
    account_age = datetime.now().astimezone() - member.created_at.astimezone()
    account_age_str = f"{account_age.days} days, {account_age.seconds // 3600} hours"
    
    content = (
        f"📥 **{member.display_name}** (`{member.id}`) joined the server\n"
        f"📅 **Account created:** {member.created_at.strftime('%Y-%m-%d %H:%M:%S')} ({account_age_str} ago)\n"
        f"👥 **Member count:** {member.guild.member_count}"
    )
    await send_log(guild_id, "member", "MEMBER JOINED", content)

@bot.event
async def on_member_remove(member):
    guild_id = member.guild.id
    
    # Get the member's roles
    roles = [role.mention for role in member.roles if role.name != "@everyone"]
    roles_text = ", ".join(roles) if roles else "None"
    
    joined_at = member.joined_at.strftime('%Y-%m-%d %H:%M:%S') if member.joined_at else "Unknown"
    
    content = (
        f"📤 **{member.display_name}** (`{member.id}`) left the server\n"
        f"📅 **Joined at:** {joined_at}\n"
        f"🎭 **Roles:** {roles_text}\n"
        f"👥 **Member count:** {member.guild.member_count}"
    )
    await send_log(guild_id, "member", "MEMBER LEFT", content)

# ==================== ADMIN COMMANDS ====================
@bot.tree.command(name="set_log_channel", description="Set a channel for a specific log category")
@app_commands.describe(
    category="The log category to configure",
    channel="The channel where logs will be sent"
)
@app_commands.choices(category=[
    app_commands.Choice(name="Voice Logs", value="voice"),
    app_commands.Choice(name="Message Logs", value="message"),
    app_commands.Choice(name="Moderation Logs", value="moderation"),
    app_commands.Choice(name="Role Logs", value="role"),
    app_commands.Choice(name="Channel Logs", value="channel"),
    app_commands.Choice(name="Member Logs", value="member")
])
async def set_log_channel(interaction: discord.Interaction, category: str, channel: discord.TextChannel):
    # Check if user has admin permissions
    if not is_admin(interaction):
        await interaction.response.send_message("You need Administrator permissions to use this command.", ephemeral=True)
        return
    
    guild_id = interaction.guild.id
    
    # Initialize guild config if not exists
    if guild_id not in guild_configs:
        guild_configs[guild_id] = {}
    
    # Set the channel for the category
    guild_configs[guild_id][category] = channel.id
    
    await interaction.response.send_message(
        f"✅ Successfully set {channel.mention} as the {category} log channel.", 
        ephemeral=True
    )
    
    # Send a test message to the channel
    await channel.send(format_log("TEST", f"This channel has been set as the **{category}** log channel."))

@bot.tree.command(name="view_log_channels", description="View currently configured log channels")
async def view_log_channels(interaction: discord.Interaction):
    # Check if user has admin permissions
    if not is_admin(interaction):
        await interaction.response.send_message("You need Administrator permissions to use this command.", ephemeral=True)
        return
    
    guild_id = interaction.guild.id
    
    if guild_id not in guild_configs or not guild_configs[guild_id]:
        await interaction.response.send_message("No log channels have been configured yet.", ephemeral=True)
        return
    
    # Build response message
    response = "**📋 Configured Log Channels:**\n\n"
    
    categories = {
        "voice": "🗣️ Voice Logs",
        "message": "💬 Message Logs",
        "moderation": "🛠️ Moderation Logs",
        "role": "🎭 Role Logs",
        "channel": "📦 Channel Logs",
        "member": "🚪 Member Logs"
    }
    
    for cat_key, cat_name in categories.items():
        if cat_key in guild_configs[guild_id]:
            channel_id = guild_configs[guild_id][cat_key]
            channel = interaction.guild.get_channel(channel_id)
            
            if channel:
                response += f"{cat_name}: {channel.mention}\n"
            else:
                response += f"{cat_name}: ⚠️ Channel not found (ID: {channel_id})\n"
        else:
            response += f"{cat_name}: ❌ Not configured\n"
    
    await interaction.response.send_message(response, ephemeral=True)

@bot.tree.command(name="remove_log_channel", description="Remove a log channel configuration")
@app_commands.describe(category="The log category to remove configuration for")
@app_commands.choices(category=[
    app_commands.Choice(name="Voice Logs", value="voice"),
    app_commands.Choice(name="Message Logs", value="message"),
    app_commands.Choice(name="Moderation Logs", value="moderation"),
    app_commands.Choice(name="Role Logs", value="role"),
    app_commands.Choice(name="Channel Logs", value="channel"),
    app_commands.Choice(name="Member Logs", value="member")
])
async def remove_log_channel(interaction: discord.Interaction, category: str):
    # Check if user has admin permissions
    if not is_admin(interaction):
        await interaction.response.send_message("You need Administrator permissions to use this command.", ephemeral=True)
        return
    
    guild_id = interaction.guild.id
    
    if guild_id not in guild_configs or category not in guild_configs[guild_id]:
        await interaction.response.send_message(f"No log channel was configured for {category}.", ephemeral=True)
        return
    
    # Remove the channel for the category
    del guild_configs[guild_id][category]
    
    await interaction.response.send_message(
        f"✅ Successfully removed the log channel configuration for {category}.", 
        ephemeral=True
    )

# Run the bot
if __name__ == "__main__":
    bot.run(TOKEN)
