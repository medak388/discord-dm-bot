# Discord Bot for Direct Messaging

A Discord bot that allows authorized users to send direct messages to individual users or entire roles within a server.

## Features

- **Slash Commands**:
  - `/send_to_user` - Send a direct message to a specific user
  - `/send_to_role` - Send a direct message to all members with a specific role
  - `/forward_to_user` - Forward an existing message to a specific user
  - `/forward_to_role` - Forward an existing message to all members with a specific role

- **Text Commands**:
  - `!send` - Send a direct message to multiple users at once

- **Permission System**:
  - Restricts command usage to a specific channel
  - Requires users to have a designated role to use commands

## Setup

### Prerequisites

- Python 3.8 or higher
- A Discord bot token
- Discord server (guild) with administrator permissions

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/discord-dm-bot.git
   cd discord-dm-bot
   ```

2. Create and activate a virtual environment:
   ```
   # Create virtual environment
   python -m venv venv

   # Activate on Windows
   venv\Scripts\activate

   # Activate on macOS/Linux
   source venv/bin/activate
   ```

3. Install the required dependencies:
   ```
   pip install --upgrade pip
   pip install discord.py python-dotenv
   ```

4. Create a `.env` file in the root directory with the following variables:
   ```
   DISCORD_API_TOKEN=your_bot_token_here
   GUILD=your_server_id_here
   ALLOWED_CHANNEL_ID=channel_id_for_bot_commands
   ALLOWED_ROLE_ID=role_id_for_authorized_users
   ```

### Getting the Required IDs

- **Bot Token**: Create a bot in the [Discord Developer Portal](https://discord.com/developers/applications) and copy the token
- **Server ID**: Right-click on your server and select "Copy ID" (Developer Mode must be enabled)
- **Channel ID**: Right-click on the channel and select "Copy ID"
- **Role ID**: Right-click on the role and select "Copy ID"

## Usage

### Starting the Bot

Run the bot with:
```
python bot.py
```

### Command Examples

#### Slash Commands

- Send a message to a user:
  ```
  /send_to_user user:@username message:Hello, this is a test message!
  ```

- Send a message to all users with a role:
  ```
  /send_to_role role:@rolename message:Important announcement for everyone with this role!
  ```

- Forward an existing message to a user:
  ```
  /forward_to_user user:@username message_link:https://discord.com/channels/server_id/channel_id/message_id
  ```

- Forward an existing message to a role:
  ```
  /forward_to_role role:@rolename message_link:https://discord.com/channels/server_id/channel_id/message_id
  ```

#### Text Command

- Send a message to multiple users:
  ```
  !send username1, username2, username3 "Your message here"
  ```

## Limitations

- The bot cannot send direct messages to users who have disabled DMs from server members
- Rate limiting may affect message delivery when sending to many users at once
- The bot must be a member of the server to deliver messages

## Troubleshooting

- If commands aren't working, make sure the bot has been added to your server with the proper permissions
- Ensure the bot has permission to read messages and send messages in the allowed channel
- Verify that all environment variables are correctly set in the `.env` file

