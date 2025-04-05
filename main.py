import tweepy
import time
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# توکن ربات تلگرام (از BotFather بگیر)
TOKEN = "7701975508:AAE_swoTzdDa_m5p087X7i2J1qoAWJhY7zU"

# لیست برای ذخیره اکانت‌ها
accounts = []
current_account = {}

# تابع شروع
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! من یه ربات برای ریپورت اکانت توییتر هستم.\n"
        "برای شروع، کلیدهای API اکانت توییترت رو وارد کن.\n"
        "مرحله ۱: API Key رو بفرست"
    )
    context.user_data["step"] = "api_key"

# تابع برای گرفتن پیام‌ها
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    step = context.user_data.get("step", "")

    if step == "api_key":
        current_account["API_KEY"] = text
        await update.message.reply_text("مرحله ۲: API Secret رو بفرست")
        context.user_data["step"] = "api_secret"

    elif step == "api_secret":
        current_account["API_SECRET"] = text
        await update.message.reply_text("مرحله ۳: Access Token رو بفرست")
        context.user_data["step"] = "access_token"

    elif step == "access_token":
        current_account["ACCESS_TOKEN"] = text
        await update.message.reply_text("مرحله ۴: Access Token Secret رو بفرست")
        context.user_data["step"] = "access_token_secret"

    elif step == "access_token_secret":
        current_account["ACCESS_TOKEN_SECRET"] = text
        accounts.append(current_account.copy())
        await update.message.reply_text(
            f"اکانت {len(accounts)} با موفقیت اضافه شد!\n"
            "اگه اکانت دیگه‌ای می‌خوای اضافه کنی، کلید API بعدی رو بفرست.\n"
            "اگه نه، نام کاربری اکانت هدف رو بفرست."
        )
        context.user_data["step"] = "api_key_or_target"

    elif step == "api_key_or_target":
        if len(accounts) > 0:
            # فرض می‌کنیم نام کاربری هدف وارد شده
            target_username = text
            await update.message.reply_text(f"در حال ریپورت کردن {target_username}...")

            # پیدا کردن ID اکانت هدف
            try:
                auth = tweepy.OAuthHandler(accounts[0]["API_KEY"], accounts[0]["API_SECRET"])
                auth.set_access_token(accounts[0]["ACCESS_TOKEN"], accounts[0]["ACCESS_TOKEN_SECRET"])
                api = tweepy.API(auth, wait_on_rate_limit=True)
                user = api.get_user(screen_name=target_username)
                user_id = user.id
            except tweepy.TweepError as e:
                await update.message.reply_text(f"خطا در پیدا کردن اکانت هدف: {e}")
                return

            # ریپورت کردن با هر اکانت
            for account in accounts:
                try:
                    auth = tweepy.OAuthHandler(account["API_KEY"], account["API_SECRET"])
                    auth.set_access_token(account["ACCESS_TOKEN"], account["ACCESS_TOKEN_SECRET"])
                    api = tweepy.API(auth, wait_on_rate_limit=True)

                    api.report_spam(user_id=user_id)
                    await update.message.reply_text(f"اکانت {target_username} با اکانت {account['ACCESS_TOKEN'][:10]}... ریپورت شد!")
                    time.sleep(random.randint(5, 15))

                except tweepy.TweepError as e:
                    await update.message.reply_text(f"خطا برای اکانت {account['ACCESS_TOKEN'][:10]}...: {e}")
                    return

            await update.message.reply_text(
                f"اکانت {target_username} با {len(accounts)} اکانت ریپورت شد!\n"
                "برای ساسپند شدن، ممکن است نیاز به ریپورت‌های بیشتری باشد.\n"
                "برای ریپورت اکانت جدید، کلید API اکانت بعدی رو بفرست یا نام کاربری جدید رو وارد کن."
            )
        else:
            current_account["API_KEY"] = text
            await update.message.reply_text("مرحله ۲: API Secret رو بفرست")
            context.user_data["step"] = "api_secret"

# تابع برای ریست کردن
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global accounts
    accounts = []
    current_account.clear()
    context.user_data["step"] = "api_key"
    await update.message.reply_text("همه اطلاعات ریست شد! لطفاً کلید API اولین اکانت رو بفرست.")

# ساخت ربات
app = Application.builder().token(TOKEN).build()

# اضافه کردن دستورات
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("reset", reset))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# اجرای ربات
print("ربات در حال اجرا است...")
app.run_polling()