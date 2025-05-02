import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, ApplicationBuilder, MessageHandler, filters
import logging
import sys
import os
from dotenv import load_dotenv
import re
import base64
from io import BytesIO
import asyncio
import aiohttp
import time

# === SET YOUR API KEYS HERE ===
BOT_TOKEN = "your_bot_token_here"
OCR_SPACE_API_KEY = "your_ocr_space_api_key_here"  # Your OCR Space API key

# Check if running on PythonAnywhere
is_pythonanywhere = 'PYTHONANYWHERE_DOMAIN' in os.environ

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Store user UID/server in memory (you can save to file/database later)
user_data = {}

# Cache for codes to reduce scraping frequency
code_cache = {
    'codes': [],
    'last_update': 0,
    'update_interval': 3600  # 1 hour
}

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

async def fetch_url(session, url, headers):
    try:
        async with session.get(url, headers=headers, timeout=10) as response:
            return await response.text()
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return None

# ===== Function to Scrape Genshin Codes =====
async def get_latest_genshin_codes():
    # Check cache first
    current_time = time.time()
    if current_time - code_cache['last_update'] < code_cache['update_interval']:
        return code_cache['codes']

    codes = set()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    async with aiohttp.ClientSession() as session:
        # Source 1: Hoyolab
        hoyolab_url = "https://www.hoyolab.com/circles/2/1"
        html = await fetch_url(session, hoyolab_url, headers)
        if html:
            soup = BeautifulSoup(html, "html.parser")
            for post in soup.find_all('div', class_='post-content'):
                text = post.get_text()
                potential_codes = re.findall(r'(?:CODE|Gift Code|Code):\s*([A-Z0-9]{5,})', text)
                codes.update(potential_codes)

        # Source 2: Genshin Impact Wiki
        wiki_url = "https://genshin-impact.fandom.com/wiki/Promotional_Codes"
        html = await fetch_url(session, wiki_url, headers)
        if html:
            soup = BeautifulSoup(html, "html.parser")
            for table in soup.find_all('table', class_='article-table'):
                for row in table.find_all('tr')[1:]:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        code = cells[0].get_text().strip()
                        if len(code) >= 5 and code.isalnum():
                            codes.add(code)

        # Source 3: Official Website
        official_url = "https://genshin.hoyoverse.com/en/news"
        html = await fetch_url(session, official_url, headers)
        if html:
            soup = BeautifulSoup(html, "html.parser")
            for article in soup.find_all(['article', 'div'], class_=['article', 'content']):
                text = article.get_text()
                potential_codes = re.findall(r'(?:CODE|Gift Code|Code):\s*([A-Z0-9]{5,})', text)
                codes.update(potential_codes)

    # Update cache
    code_cache['codes'] = list(codes)
    code_cache['last_update'] = current_time
    return code_cache['codes']

# Function to generate redeem link
def generate_redeem_link(code: str, uid: str = None, server: str = None) -> str:
    base_url = "https://genshin.hoyoverse.com/en/gift"
    if uid and server:
        return f"{base_url}?code={code}&uid={uid}&region={server}"
    return f"{base_url}?code={code}"

# ===== Bot Commands =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    uid_info = user_data.get(user_id)
    if uid_info:
        uid_text = f"\n✅ Your UID: {uid_info['uid']} (Server: {uid_info['server']})"
    else:
        uid_text = ""
    await update.message.reply_text(
        "🎮 Welcome to the Genshin Gift Bot!\n\n"
        "🔹 Send a gift code like `GENSHINGIFT`\n"
        "🔹 Use /redeem to get the latest gift codes and redeem them instantly.\n"
        "🔹 Send a photo of the gift code to the bot to scan it.\n"
        "🔹 Use /setuid <your UID> to auto-fill redemption link\n"
        f"{uid_text}\n\n"
        "Example:\n/setuid 858969293"
    )

async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Send a loading message
        loading_message = await update.message.reply_text(
            "⏳ Đang tìm kiếm gift code mới nhất...\n"
            "Vui lòng đợi một chút nhé! 🎮"
        )

        codes = await get_latest_genshin_codes()
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
        logger.error(f"Error in redeem function: {e}")
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
    try:
        # Get the photo file
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()

        # Convert image to base64 with proper format
        image_base64 = f"data:image/jpeg;base64,{base64.b64encode(photo_bytes).decode('utf-8')}"

        # Prepare OCR Space API request
        url = "https://api.ocr.space/parse/image"
        payload = {
            "apikey": OCR_SPACE_API_KEY,
            "base64Image": image_base64,
            "language": "eng",
            "OCREngine": 2,  # Use OCR Engine 2 for better accuracy
            "filetype": "JPG"  # Specify file type
        }

        # Send request to OCR Space API
        response = requests.post(url, data=payload)
        result = response.json()

        if result.get("IsErroredOnProcessing"):
            error_message = result.get("ErrorMessage", "Unknown error")
            logger.error(f"OCR Space API error: {error_message}")
            await update.message.reply_text(
                "❌ Lỗi khi xử lý ảnh.\n\n"
                "Có thể do:\n"
                "1️⃣ Ảnh không rõ nét\n"
                "2️⃣ API key không hợp lệ\n"
                "3️⃣ Lỗi kết nối với OCR Space\n\n"
                "Vui lòng thử lại với ảnh rõ nét hơn hoặc gửi code dưới dạng text."
            )
            return

        # Extract text from OCR result
        text = ""
        if result.get("ParsedResults"):
            text = result["ParsedResults"][0].get("ParsedText", "").strip()

        if text:
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
            await update.message.reply_text("⚠️ Không tìm thấy text trong ảnh. Vui lòng thử lại với ảnh rõ nét hơn.")

    except Exception as e:
        logger.error(f"Error processing photo: {e}")
        await update.message.reply_text(
            "❌ Có lỗi xảy ra khi xử lý ảnh.\n\n"
            "Vui lòng thử lại hoặc gửi code dưới dạng text."
        )

# ===== Main App Setup =====
def main():
    # Remove development mode check
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("redeem", redeem))
    app.add_handler(CommandHandler("setuid", set_uid))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("✅ Bot is running... Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()
