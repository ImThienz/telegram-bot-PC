const { Telegraf } = require('telegraf')
const { exec } = require('child_process');
require('dotenv').config();

const BOT_TOKEN = process.env.BOT_TOKEN

const bot = new Telegraf(BOT_TOKEN)
bot.start((ctx) => ctx.reply(
`Chào mừng bạn đến với Shutdown Bot! 🚀

Các lệnh có sẵn:
/sd hoặc /shutdown - Tắt máy tính
/rs hoặc /restart - Khởi động lại máy tính
/sl hoặc /sleep - Đưa máy tính vào chế độ ngủ

⚠️ Lưu ý: Tất cả các lệnh sẽ có thời gian chờ 5 giây trước khi thực hiện.`
))
bot.command('sd' || 'shutdown', (ctx) => {
    const time = 5

    // shutdown in [time] seconds
    const cmd = `shutdown -s -f -t ${time}`

    exec(cmd, (error) => {
        if (error) {
            console.error(`exec error: ${error}`);
            return;
        }
    });

    if (time > 0) {
        ctx.reply(`Máy tính sẽ tắt sau ${time} giây.`)
    } else {
        ctx.reply('Máy tính sẽ tắt ngay lập tức.')
    }
})

bot.command('rs' || 'restart', (ctx) => {
    const time = 5;

    // restart in [time] seconds
    const cmd = `shutdown -r -f -t ${time}`;

    exec(cmd, (error) => {
        if (error) {
            console.error(`exec error: ${error}`);
            return;
        }
    });

    if (time > 0) {
        ctx.reply(`Máy tính sẽ khởi động lại sau ${time} giây.`);
    } else {
        ctx.reply('Máy tính sẽ khởi động lại ngay lập tức.');
    }
});

bot.command('sl' || 'sleep', (ctx) => {
    const cmd = 'rundll32.exe powrprof.dll,SetSuspendState 0,1,0';

    exec(cmd, (error) => {
        if (error) {
            console.error(`exec error: ${error}`);
            return;
        }
    });

    ctx.reply('Máy tính sẽ vào chế độ sleep.');
});

bot.launch()

// Enable graceful stop
process.once('SIGINT', () => bot.stop('SIGINT'))
process.once('SIGTERM', () => bot.stop('SIGTERM'))

console.log('Bot started')