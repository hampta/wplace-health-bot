![Wplace Logo](https://cdn.discordapp.com/attachments/1404426499959947305/1404433909164412990/download_1_1.png?ex=689b2c81&is=6899db01&hm=3d9140d16616c482c8325a9aab66747fed514a0cb8e3016fd624e03116c1d53f&)

# WPlace Health Bot

<a href="https://t.me/wplace_health"><img  src="https://img.shields.io/badge/TELEGRAM-Channel-blue?style=for-the-badge" /></a>

This bot monitors the health of a backend service and sends notifications to Discord and Telegram when the service status changes.

## How to Use
1. **Clone the repository**:
   ```bash
   git clone github.com/hampta/wplace-health-bot.git
   cd wplace-health-bot
    ```
2. **Set up environment variables**:
   Rename `.env.example` to `.env` and fill in the required values:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file with your Discord and Telegram configurations.
3. **Install dependencies**:
   ```bash
   uv sync
   ```
4. **Run the bot**:
   ```bash
   uv run main.py
   ```


# License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details