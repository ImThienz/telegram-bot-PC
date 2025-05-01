import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, ApplicationBuilder, MessageHandler, filters
import logging
import sys
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv
import re

# script to send a letter from pic
import pytesseract
from PIL import Image
from io import BytesIO

# Load environment variables from config/GI-bot/.env
load_dotenv(os.path.join('config', 'GI-bot', '.env'))

# Set Tesseract path - Update this to your actual Tesseract installation path
# Common paths:
# C:\Program Files\Tesseract-OCR\tesseract.exe
# C:\Program Files (x86)\Tesseract-OCR\tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# === SET YOUR BOT TOKEN HERE ===
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Optional: Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Store user UID/server in memory (you can save to file/database later)
user_data = {}

# File change handler for development mode
class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('genshin_bot.py'):
            print("\n🔄 Code changed, restarting bot...")
            os.execv(sys.executable, ['python'] + sys.argv)

# Server detection from UID prefix
def detect_server(uid: str) -> str:
    if uid.startswith("1") or uid.startswith("2"):
        return "os_usa"
    elif uid.startswith("6") or uid.startswith("7"):
        return "os_euro"
    elif uid.startswith("8") or uid.startswith("9"):
        return "os_asia"
    elif uid.startswith("5"):
        return "os_cht"
    return "os_asia"

# ===== Function to Scrape Genshin Codes =====
def get_latest_genshin_codes():
    codes = set()  # Use set to avoid duplicates
    
    try:
        # Source 1: Hoyolab
        hoyolab_url = "https://www.hoyolab.com/circles/2/1"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(hoyolab_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Look for code patterns in Hoyolab posts
        for post in soup.find_all('div', class_='post-content'):
            text = post.get_text()
            # Look for patterns like "CODE: XXXXXXXX" or "Gift Code: XXXXXXXX"
            potential_codes = re.findall(r'(?:CODE|Gift Code|Code):\s*([A-Z0-9]{8,})', text)
            codes.update(potential_codes)
    
    except Exception as e:
        print(f"Error scraping Hoyolab: {e}")
    
    try:
        # Source 2: Genshin Impact Wiki
        wiki_url = "https://genshin-impact.fandom.com/wiki/Promotional_Codes"
        response = requests.get(wiki_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Look for code tables
        for table in soup.find_all('table', class_='article-table'):
            for row in table.find_all('tr')[1:]:  # Skip header row
                cells = row.find_all('td')
                if len(cells) >= 2:
                    code = cells[0].get_text().strip()
                    if len(code) >= 8 and code.isalnum():
                        codes.add(code)
    
    except Exception as e:
        print(f"Error scraping Wiki: {e}")
    
    try:
        # Source 3: Genshin Impact Subreddit
        reddit_url = "https://www.reddit.com/r/Genshin_Impact/search.json?q=flair_name%3A%22Code%22&restrict_sr=1&sort=new"
        response = requests.get(reddit_url, headers=headers, timeout=10)
        data = response.json()
        
        for post in data.get('data', {}).get('children', []):
            title = post['data']['title']
            # Look for codes in titles
            potential_codes = re.findall(r'[A-Z0-9]{8,}', title)
            codes.update(potential_codes)
    
    except Exception as e:
        print(f"Error scraping Reddit: {e}")
    
    return list(codes)

# Function to generate redeem link
def generate_redeem_link(code: str, uid: str = None, server: str = None) -> str:
    base_url = "https://genshin.hoyoverse.com/en/gift"
    if uid and server:
        return f"{base_url}?code={code}&uid={uid}&region={server}"
    return f"{base_url}?code={code}"

# ===== Bot Commands =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 Welcome to the Genshin Gift Bot!\n\n"
        "🔹 Send a gift code like `GENSHINGIFT`\n"
        "🔹 Use /redeem to get the latest gift codes and redeem them instantly.\n"
        "🔹 Send a photo of the gift code to the bot to scan it.\n"
        "🔹 Use /setuid <your UID> to auto-fill redemption link\n\n"
        "Example:\n/setuid 858969293"
    )

async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Send a loading message
        loading_message = await update.message.reply_text(
            "⏳ Đang tìm kiếm gift code mới nhất...\n"
            "Vui lòng đợi một chút nhé! 🎮"
        )

        codes = get_latest_genshin_codes()
        if not codes:
            await loading_message.edit_text(
                "😢 Hiện tại không có gift code nào mới.\n\n"
                "Bạn có thể:\n"
                "1️⃣ Theo dõi trang chủ Genshin Impact\n"
                "2️⃣ Tham gia cộng đồng Genshin Impact Việt Nam\n"
                "3️⃣ Kiểm tra lại sau ít phút\n\n"
                "Bot sẽ tự động cập nhật khi có code mới! 🎁"
            )
            return

        # Get user's UID and server if set
        user_id = update.effective_user.id
        uid_info = user_data.get(user_id)
        
        # Create keyboard with redeem buttons
        keyboard = []
        for code in codes:
            if uid_info:
                link = generate_redeem_link(code, uid_info['uid'], uid_info['server'])
                keyboard.append([InlineKeyboardButton(f"🎮 Redeem {code}", url=link)])
            else:
                link = generate_redeem_link(code)
                keyboard.append([InlineKeyboardButton(f"🎮 Redeem {code}", url=link)])
        
        # Add Hoyolab button
        keyboard.append([InlineKeyboardButton("📱 Theo dõi Hoyolab", url="https://www.hoyolab.com/circles/2/1")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Format message with codes
        message = "🎉 Tìm thấy gift code mới!\n\n"
        message += "📝 Danh sách code:\n"
        for i, code in enumerate(codes, 1):
            message += f"{i}. `{code}`\n"
        
        message += "\n🎮 Cách sử dụng:\n"
        message += "1️⃣ Nhấn vào nút Redeem tương ứng với code bạn muốn\n"
        message += "2️⃣ Đăng nhập tài khoản của bạn\n"
        if uid_info:
            message += "3️⃣ UID và server đã được tự động điền\n"
        else:
            message += "3️⃣ Nhập UID của bạn\n"
        message += "4️⃣ Nhấn Redeem để nhận quà\n\n"
        
        message += "⚠️ Lưu ý quan trọng:\n"
        message += "• Gift code có thể hết hạn sớm\n"
        message += "• Mỗi tài khoản chỉ nhận được một lần\n"
        message += "• Vui lòng kiểm tra server trước khi nhập code\n"
        message += "• Nếu code không hoạt động, có thể đã hết hạn\n\n"
        
        if not uid_info:
            message += "💡 Mẹo nhỏ:\n"
            message += "• Sử dụng /setuid <UID> để tự động điền UID\n"
            message += "• Ví dụ: /setuid 123456789\n\n"
        
        message += "Chúc bạn may mắn! 🍀"

        await loading_message.edit_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    except Exception as e:
        print(f"Error in redeem function: {e}")
        await update.message.reply_text(
            "❌ Có lỗi xảy ra khi tìm gift code.\n\n"
            "Bạn có thể thử:\n"
            "1️⃣ Kiểm tra kết nối mạng\n"
            "2️⃣ Thử lại sau ít phút\n"
            "3️⃣ Liên hệ admin nếu lỗi vẫn tiếp diễn\n\n"
            "Xin lỗi vì sự bất tiện này! 😢"
        )

# /setuid command
async def set_uid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usage: /setuid <your 9-digit UID>")
        return

    uid = context.args[0]
    if not uid.isdigit() or len(uid) != 9:
        await update.message.reply_text("⚠️ Invalid UID. Must be 9 digits.")
        return

    server = detect_server(uid)
    user_id = update.effective_user.id
    user_data[user_id] = {'uid': uid, 'server': server}
    await update.message.reply_text(f"✅ UID saved: {uid} (Server: {server})")

# Handle gift code text messages
async def handle_code_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().upper()
    codes = [code.strip() for code in text.split('\n')]
    
    base_url = "https://genshin.hoyoverse.com/en/gift"
    user_id = update.effective_user.id
    uid_info = user_data.get(user_id)

    for code in codes:
        if not code.isalnum() or len(code) < 8:
            continue  # Skip invalid codes

        if uid_info:
            uid = uid_info['uid']
            server = uid_info['server']
            link = f"{base_url}?code={code}&uid={uid}&region={server}"
            await update.message.reply_text(
                f"🎁 Redeem this code:\n🔗 {link}\n\n✅ UID and region auto-filled!"
            )
        else:
            link = f"{base_url}?code={code}"
            await update.message.reply_text(
                f"🎁 Redeem this code:\n🔗 {link}\n\nℹ️ Use /setuid <your UID> for auto-fill next time."
            )

# Handle photos: OCR scan
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    photo_bytes = await photo_file.download_as_bytearray()

    try:
        image = Image.open(BytesIO(photo_bytes))
        text = pytesseract.image_to_string(image)
        
        if text.strip():
            # Split text into lines and process each code
            codes = [code.strip() for code in text.split('\n') if code.strip()]
            base_url = "https://genshin.hoyoverse.com/en/gift"
            user_id = update.effective_user.id
            uid_info = user_data.get(user_id)

            for code in codes:
                if not code.isalnum() or len(code) < 5:
                    continue  # Skip invalid codes

                if uid_info:
                    uid = uid_info['uid']
                    server = uid_info['server']
                    link = f"{base_url}?code={code}&uid={uid}&region={server}"
                    await update.message.reply_text(
                        f"🎁 Redeem this code:\n🔗 {link}\n\n✅ UID and region auto-filled!"
                    )
                else:
                    link = f"{base_url}?code={code}"
                    await update.message.reply_text(
                        f"🎁 Redeem this code:\n🔗 {link}\n\nℹ️ Use /setuid <your UID> for auto-fill next time."
                    )
        else:
            await update.message.reply_text("⚠️ Couldn't find any readable text in that image.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error processing image:\n{str(e)}")

# ===== Main App Setup =====
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("redeem", redeem))
    app.add_handler(CommandHandler("setuid", set_uid))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Set up file watching in development mode
    if '--dev' in sys.argv:
        print("🔧 Running in development mode with auto-reload")
        observer = Observer()
        observer.schedule(FileChangeHandler(), path='.', recursive=False)
        observer.start()

    print("✅ Bot is running... Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()