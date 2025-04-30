# Genshin Impact Gift Code Bot

A Telegram bot that helps you redeem Genshin Impact gift codes.

## Installation

1. Clone this repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Tesseract OCR:
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install and note the installation path
4. Create a `.env` file with your bot token:
   ```
   BOT_TOKEN=your_bot_token_here
   ```
5. Update the Tesseract path in `genshin_bot.py` if needed:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

## Usage

Run the bot:
```bash
python genshin_bot.py
```

For development mode with auto-reload:
```bash
python genshin_bot.py --dev
```

## Features

- Scan gift codes from images
- Get latest gift codes
- Auto-fill UID and server for redemption
- Support multiple servers (Asia, Europe, America, etc.)

## Commands

- `/start` - Show welcome message
- `/redeem` - Get latest gift codes
- `/setuid <your_uid>` - Set your UID for auto-fill
- Send a photo of gift code to scan
- Send gift code text to get redemption link
