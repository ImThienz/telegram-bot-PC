import os
import subprocess
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Setup logging
logging.basicConfig(
    filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bot.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# === SET YOUR BOT TOKEN HERE ===
BOT_TOKEN="put-your-token-controll-PC-here"

# Store user names
user_names = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    user_names[user_id] = user_name
    
    logging.info(f"Start command received from user {user_id} ({user_name})")
    await update.message.reply_text(
        f"Chào mừng {user_name} đến với PC Control Bot! 🚀\n\n"
        "Các lệnh có sẵn:\n"
        "/sd hoặc /shutdown - Tắt máy tính\n"
        "/rs hoặc /restart - Khởi động lại máy tính\n"
        "/sl hoặc /sleep - Đưa máy tính vào chế độ ngủ\n\n"
        "⚠️ Lưu ý: Bot đang chạy trên máy tính của bạn."
    )

async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.message.text.strip()
    user_names[user_id] = user_name
    
    logging.info(f"User {user_id} set name to {user_name}")
    await update.message.reply_text(
        f"✅ Tên của bạn đã được cập nhật thành: {user_name}\n\n"
        "Bạn có thể sử dụng các lệnh:\n"
        "/sd hoặc /shutdown - Tắt máy tính\n"
        "/rs hoặc /restart - Khởi động lại máy tính\n"
        "/sl hoặc /sleep - Đưa máy tính vào chế độ ngủ"
    )

async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = user_names.get(user_id, "Người dùng")
    
    logging.info(f"Shutdown command received from user {user_id} ({user_name})")
    await update.message.reply_text(f"⏳ {user_name}, máy tính sẽ tắt sau 5 giây...")
    
    # Delay 3 seconds before executing shutdown
    await asyncio.sleep(3)
    
    try:
        # Windows command to shutdown
        subprocess.run("shutdown -s -t 5", shell=True)
        await update.message.reply_text(f"✅ {user_name}, máy tính sẽ tắt sau 5 giây.")
        logging.info(f"Shutdown command executed successfully for user {user_name}")
    except Exception as e:
        error_msg = f"❌ Lỗi khi tắt máy: {str(e)}"
        logging.error(error_msg)
        await update.message.reply_text(error_msg)

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = user_names.get(user_id, "Người dùng")
    
    logging.info(f"Restart command received from user {user_id} ({user_name})")
    await update.message.reply_text(f"⏳ {user_name}, máy tính sẽ khởi động lại sau 5 giây...")
    
    # Delay 3 seconds before executing restart
    await asyncio.sleep(3)
    
    try:
        # Windows command to restart
        subprocess.run("shutdown -r -t 5", shell=True)
        await update.message.reply_text(f"✅ {user_name}, máy tính sẽ khởi động lại sau 5 giây.")
        logging.info(f"Restart command executed successfully for user {user_name}")
    except Exception as e:
        error_msg = f"❌ Lỗi khi khởi động lại: {str(e)}"
        logging.error(error_msg)
        await update.message.reply_text(error_msg)

async def sleep(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = user_names.get(user_id, "Người dùng")
    
    logging.info(f"Sleep command received from user {user_id} ({user_name})")
    await update.message.reply_text(f"⏳ {user_name}, máy tính sẽ vào chế độ sleep...")
    
    # Delay 3 seconds before executing sleep
    await asyncio.sleep(3)
    
    try:
        # Windows command to sleep
        subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
        await update.message.reply_text(f"✅ {user_name}, máy tính sẽ vào chế độ sleep.")
        logging.info(f"Sleep command executed successfully for user {user_name}")
    except Exception as e:
        error_msg = f"❌ Lỗi khi vào chế độ sleep: {str(e)}\n\n Bạn vừa đánh thức máy phải không, {user_name}?"
        logging.error(error_msg)
        await update.message.reply_text(error_msg)

def main():
    try:
        # Create the Application
        app = Application.builder().token(BOT_TOKEN).build()
        logging.info("Bot application created")

        # Add handlers
        app.add_handler(CommandHandler(["start"], start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name))
        app.add_handler(CommandHandler(["sd", "shutdown"], shutdown))
        app.add_handler(CommandHandler(["rs", "restart"], restart))
        app.add_handler(CommandHandler(["sl", "sleep"], sleep))
        logging.info("Handlers added")

        # Start the bot
        logging.info("Starting bot polling...")
        print("Bot started...")
        app.run_polling()
    except Exception as e:
        logging.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main() 