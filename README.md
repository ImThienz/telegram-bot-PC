# PC Control Telegram Bot

Một bot Telegram đơn giản để điều khiển máy tính Windows từ xa thông qua các lệnh Telegram.

## ⚠️ CẢNH BÁO QUAN TRỌNG

### Cảnh báo về quyền truy cập
- Bot yêu cầu quyền Administrator để thực thi các lệnh hệ thống
- Không đặt script trong các thư mục hệ thống (như C:\Windows, C:\Program Files)
- Không chạy script từ các thư mục yêu cầu quyền đặc biệt
- Đề xuất: Đặt script trong thư mục người dùng (ví dụ: D:\script)

### Tuyên bố miễn trừ trách nhiệm
- Bot này được cung cấp "NHƯ LÀ" (AS IS) và không có bất kỳ bảo đảm nào
- Người dùng tự chịu trách nhiệm về việc sử dụng bot
- Tác giả không chịu trách nhiệm về bất kỳ thiệt hại nào có thể xảy ra
- Người dùng nên hiểu rõ các lệnh trước khi sử dụng
- Không sử dụng bot trên các máy tính quan trọng hoặc chứa dữ liệu nhạy cảm

## Tính năng

- 🔐 Bảo mật: Bot chỉ chạy trên máy tính của bạn
- 🚀 Điều khiển từ xa: Tắt, khởi động lại hoặc đưa máy tính vào chế độ ngủ
- 👤 Cá nhân hóa: Lưu và hiển thị tên người dùng trong các thông báo
- ⏱️ Thông báo thời gian thực: Hiển thị thông báo trước và sau khi thực thi lệnh
- 📝 Ghi log: Tự động ghi lại tất cả các hoạt động vào file log

## Các lệnh

- `/start` - Khởi động bot và hiển thị menu lệnh
- `/sd` hoặc `/shutdown` - Tắt máy tính
- `/rs` hoặc `/restart` - Khởi động lại máy tính
- `/sl` hoặc `/sleep` - Đưa máy tính vào chế độ ngủ

## Cài đặt

1. Cài đặt Python 3.7 trở lên
2. Cài đặt các thư viện cần thiết:
   ```bash
   pip install python-telegram-bot
   ```
3. Tạo bot Telegram thông qua [@BotFather](https://t.me/BotFather) và lấy token
4. Cập nhật `BOT_TOKEN` trong file `PC-bot.py`
5. **QUAN TRỌNG**: Đặt script trong thư mục không yêu cầu quyền đặc biệt

## Chạy bot

### Chạy trực tiếp
```bash
python PC-bot.py
```

### Chạy như một service Windows
1. Chạy file `create_service.bat` với quyền Administrator
2. Service sẽ tự động khởi động cùng Windows

## Cấu hình service

- Tên service: `PCBotService2`
- Hiển thị tên: `PC Control Bot Service 2`
- Mô tả: `Telegram bot service for controlling PC`
- Tự động khởi động cùng Windows

## Quản lý service

### Cài đặt service
```bash
create_service.bat
```

### Gỡ cài đặt service
```bash
uninstall_service.bat
```

## Tính năng mới

### Thông báo thời gian thực
- Bot sẽ hiển thị thông báo trước khi thực thi lệnh
- Delay 3 giây trước khi thực thi để người dùng có thể hủy nếu cần
- Thông báo xác nhận sau khi lệnh được thực thi

### Cá nhân hóa
- Lưu tên người dùng từ Telegram
- Hiển thị tên người dùng trong tất cả các thông báo
- Thông báo lỗi thân thiện với người dùng

### Ghi log
- Tự động ghi lại tất cả các hoạt động vào file `bot.log`
- Bao gồm thông tin người dùng, lệnh và kết quả thực thi
- Hỗ trợ debug và theo dõi hoạt động

## Bảo mật

- Bot chỉ chạy trên máy tính của bạn
- Không lưu trữ thông tin nhạy cảm
- Tất cả các lệnh đều yêu cầu xác nhận trước khi thực thi
- **KHÔNG** đặt script trong các thư mục hệ thống
- **KHÔNG** chia sẻ token bot với người khác

## Lưu ý

- Đảm bảo chạy bot với quyền Administrator để có thể thực thi các lệnh hệ thống
- Kiểm tra file log nếu gặp lỗi
- Không chia sẻ token bot với người khác
- **QUAN TRỌNG**: Đọc kỹ các cảnh báo và tuyên bố miễn trừ trách nhiệm trước khi sử dụng

### Demo Video
https://vt.tiktok.com/ZSFpqHQJT/

### Requirements
1. [Node.js](https://nodejs.org/)
2. [npm](https://www.npmjs.com/) (installed with Node.js by default)
3. Telegram bot token

### How to use
1. Clone the repository (or download the zip file)
2. Install the required packages using `npm install` (or `yarn install`)
3. Create a new bot using [BotFather](https://t.me/BotFather) on Telegram
4. Copy the token and paste it in the `index.js` file
5. Run the bot using `node index.js`
6. Send `/sd` or `/shutdown` to the bot to shutdown your computer

### Follow me on TikTok
https://www.tiktok.com/@juno_okyo


## On Project, open CMD and run
`npm init -y`  
`npm install telegraf dotenv`  
`node index.js`

## Branch:
`[main]`: For PC controller  
`[GI-bot]`: For auto create link giftcode Genshin Impact
