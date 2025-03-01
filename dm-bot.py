import asyncio
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import app_commands
import re 

load_dotenv()

# Environment variables
DISCORD_API_SECRET = os.getenv("DISCORD_API_TOKEN")
GUILD_ID = os.getenv("GUILD")
ALLOWED_CHANNEL_ID = os.getenv("ALLOWED_CHANNEL_ID")
ALLOWED_ROLE_ID = os.getenv("ALLOWED_ROLE_ID")

# Validate environment variables
if not all([DISCORD_API_SECRET, GUILD_ID, ALLOWED_CHANNEL_ID, ALLOWED_ROLE_ID]):
    raise EnvironmentError("All environment variables must be set in the .env file")

# Initialize bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot is ready as {bot.user}")
    try:
        await bot.tree.sync()
        print("Commands synced")
    except Exception as e:
        print(f"Sync failed: {e}")

async def check_permissions(interaction: discord.Interaction) -> bool:
    """Check if user has permission to use commands"""
    if interaction.channel_id != int(ALLOWED_CHANNEL_ID):
        await interaction.response.send_message("This command can only be used in the designated channel.", ephemeral=True)
        return False

    member = interaction.guild.get_member(interaction.user.id)
    allowed_role = discord.utils.get(interaction.guild.roles, id=int(ALLOWED_ROLE_ID))
    if allowed_role not in member.roles:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return False
    return True

@bot.tree.command(name="send_to_user")
@app_commands.describe(user="Target user", message="Message to send")
async def send_to_user(interaction: discord.Interaction, user: discord.User, message: str):
    if not await check_permissions(interaction):
        return

    try:
        await user.send(message)
        await interaction.response.send_message(f"Message sent to {user.mention}", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Failed to send message to {user.mention}", ephemeral=True)

@bot.tree.command(name="send_to_role")
@app_commands.describe(role="Target role", message="Message to send")
async def send_to_role(interaction: discord.Interaction, role: discord.Role, message: str):
    if not await check_permissions(interaction):
        return

    await interaction.response.defer(ephemeral=True)
    
    failed_members = []
    success_count = 0

    for member in role.members:
        try:
            await member.send(message)
            success_count += 1
            await asyncio.sleep(0.5)  # Rate limiting
        except:
            failed_members.append(member.name)

    status = f"Sent to {success_count}/{len(role.members)} members"
    if failed_members:
        status += f"\nFailed: {', '.join(failed_members)}"

    await interaction.followup.send(status, ephemeral=True)

@bot.tree.command(name="forward_to_role")
@app_commands.describe(
    role="Target role",
    message_link="Message link to forward"
)
async def forward_to_role(interaction: discord.Interaction, role: discord.Role, message_link: str):
    if not await check_permissions(interaction):
        return

    try:
        parts = message_link.split('/')
        if len(parts) < 7:
            await interaction.response.send_message("Invalid message link", ephemeral=True)
            return

        channel_id = int(parts[-2])
        message_id = int(parts[-1])
        
        channel = interaction.guild.get_channel(channel_id)
        if not channel:
            await interaction.response.send_message("Channel not found", ephemeral=True)
            return

        message = await channel.fetch_message(message_id)
        
        await interaction.response.defer(ephemeral=True)
        
        failed_members = []
        success_count = 0

        for member in role.members:
            try:
                # Send embeds if they exist
                if message.embeds:
                    await member.send(embed=message.embeds[0])
                
                # Send content if it exists
                if message.content:
                    await member.send(content=message.content)
                
                # Send attachments if they exist
                if message.attachments:
                    for attachment in message.attachments:
                        await member.send(attachment.url)
                
                success_count += 1
                await asyncio.sleep(0.5)  # Rate limiting
            except Exception as e:
                failed_members.append(member.name)

        status = f"Forwarded to {success_count}/{len(role.members)} members"
        if failed_members:
            status += f"\nFailed: {', '.join(failed_members)}"

        await interaction.followup.send(status, ephemeral=True)

    except Exception as e:
        await interaction.followup.send("Failed to forward message", ephemeral=True)

@bot.tree.command(name="forward_to_user")
@app_commands.describe(
    user="User to receive the message",
    message_link="Message link to forward"
)
async def forward_to_user(interaction: discord.Interaction, user: discord.User, message_link: str):
    if not await check_permissions(interaction):
        return

    try:
        parts = message_link.split('/')
        if len(parts) < 7:
            await interaction.response.send_message("Invalid message link", ephemeral=True)
            return

        channel_id = int(parts[-2])
        message_id = int(parts[-1])
        
        channel = interaction.guild.get_channel(channel_id)
        if not channel:
            await interaction.response.send_message("Channel not found", ephemeral=True)
            return

        message = await channel.fetch_message(message_id)
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Send embeds if they exist
            if message.embeds:
                await user.send(embed=message.embeds[0])
            
            # Send content if it exists
            if message.content:
                await user.send(content=message.content)
            
            # Send attachments if they exist
            if message.attachments:
                for attachment in message.attachments:
                    await user.send(attachment.url)
            
            await interaction.followup.send(f"Successfully forwarded message to {user.mention}", ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"Failed to forward message to {user.mention}", ephemeral=True)

    except Exception as e:
        await interaction.followup.send("Failed to forward message", ephemeral=True)

@bot.command()
async def send(ctx, *, arg):
    """Send a DM to specified users with the provided message."""
    if ctx.channel.id != int(ALLOWED_CHANNEL_ID):
        await ctx.send("This command can only be used in the designated channel.")
        return

    # Check if user has the required role
    role = discord.utils.get(ctx.guild.roles, id=int(ALLOWED_ROLE_ID))
    if role not in ctx.author.roles:
        await ctx.send("You do not have permission to use this command.")
        return

    # Use regex to split usernames and message enclosed in quotes
    match = re.match(r"^(.+?)\s+\"(.+)\"$", arg)
    if not match:
        await ctx.send("Please provide the usernames and message in the correct format.")
        return

    usernames_str, message = match.groups()
    usernames = [user.strip() for user in usernames_str.split(',')]  # Split by comma and strip spaces

    # Get the guild by ID
    guild = discord.utils.get(bot.guilds, id=int(GUILD_ID))
    if not guild:
        await ctx.send("Guild not found.")
        return

    sent_count = 0
    failed_users = []

    for username in usernames:
        if not username:  # Skip empty usernames
            continue
        user = discord.utils.get(guild.members, name=username)
        if user:
            try:
                await user.send(message)  # Send the provided message
                sent_count += 1
            except:
                failed_users.append(user.name)
        else:
            failed_users.append(username)

    # Prepare the response message
    response = f"Successfully sent messages to {sent_count} user(s)."
    if failed_users:
        response += f"\nFailed to send messages to: {', '.join(failed_users)}"

    await ctx.send(response)
    
if __name__ == "__main__":
    bot.run(DISCORD_API_SECRET)



# cd path_to_your_directory                 # Navigate to your project directory
# python -m venv venv                       # Create a virtual environment
# # Activate the virtual environment
# venv\Scripts\activate                      # Windows
# source venv/bin/activate                   # macOS/Linux
# pip install --upgrade pip                  # Upgrade pip
# pip install discord.py python-dotenv       # Install required packages
# touch .env                                 # Create .env file (macOS/Linux)
# echo.> .env                                # Create .env file (Windows)
# pip freeze > requirements.txt              # Create requirements.txt (optional)
# python your_bot_file.py                    # Run your bot script

#.env file :
#DISCORD_API_TOKEN=''                        #bot Token 
#GUILD=''                                    #Server id
#ALLOWED_CHANNEL_ID=''                       #ALLOWED_CHANNEL_ID
#ALLOWED_ROLE_ID=''                          #ALLOWED_ROLE_ID
