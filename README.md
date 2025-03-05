# Discord-Bot
# Discord Bot

A feature-rich Discord bot built with Python that supports AI-powered responses, reminders, polls, and user-specific time zones.

## Features
- 🤖 **AI Mode**: Users can enable AI mode to chat with the bot using the Gemini API.
- ⏰ **Reminders**: Users can set, delete, and manage reminders based on their time zones.
- 🌍 **User-Specific Time Zones**: Users can set their preferred time zones for accurate reminders.
- 📊 **Polls**: Users can create polls with 2-10 options.
- 🔄 **Admin Controls**: Admins can restart or stop the bot.

## Setup Instructions

### Prerequisites
- Python 3.10+
- A Discord bot token
- A Gemini API key
- Required Python packages

### Installation
1. Clone this repository:
   ```sh
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Create a `.env` file and add:
   ```ini
   DISCORD_BOT_TOKEN=your_discord_token
   GEMINI_API_KEY=your_gemini_api_key
   ```

### Running the Bot
```sh
python bot.py
```

## Commands

### AI Mode
- `!mode ai` → Enable AI responses.
- `!mode normal` → Disable AI responses.

### Reminders
- `!settimezone <timezone>` → Set your preferred time zone.
- `!remind <HH:MM> <message>` → Set a reminder.
- `!delreminder` → Delete your active reminder.

### Polls
- `!poll <question> <option1> <option2> ... <option10>` → Create a poll.

### Admin Commands
- `!restart` → Restart the bot.
- `!stop` → Stop the bot.

