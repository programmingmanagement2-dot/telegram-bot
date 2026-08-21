import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from config import BOT_TOKEN
from services import SERVICES


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛍️ Services", callback_data="services")],
        [InlineKeyboardButton("📦 My Orders", callback_data="orders")],
        [InlineKeyboardButton("💳 Payment", callback_data="payment")],
        [InlineKeyboardButton("📞 Support", callback_data="support")],
    ]

    await update.message.reply_text(
        "👋 Welcome to GrowthMate AI!\n\n"
        "🚀 Digital Growth & Development Services\n\n"
        "Choose an option below:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "services":
        keyboard = []

        for service_id, service in SERVICES.items():
            keyboard.append([
                InlineKeyboardButton(
                    service["name"],
                    callback_data=f"service_{service_id}"
                )
            ])

        keyboard.append([
            InlineKeyboardButton("⬅️ Back", callback_data="back")
        ])

        await query.edit_message_text(
            "🛍️ *Our Services*\n\n"
            "Select a service:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

    elif query.data.startswith("service_"):
        service_id = query.data.replace("service_", "")
        service = SERVICES.get(service_id)

        if not service:
            await query.edit_message_text("❌ Service not found.")
            return

        keyboard = [
            [InlineKeyboardButton(
                "💳 Order / Payment",
                callback_data=f"buy_{service_id}"
            )],
            [InlineKeyboardButton(
                "⬅️ Back to Services",
                callback_data="services"
            )],
        ]

        await query.edit_message_text(
            f"📌 *{service['name']}*\n\n"
            f"{service['description']}\n\n"
            f"💰 Starting Price: ₹{service['price']}\n\n"
            "Tap below to continue.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

    elif query.data.startswith("buy_"):
        service_id = query.data.replace("buy_", "")
        service = SERVICES.get(service_id)

        if not service:
            await query.edit_message_text("❌ Service not found.")
            return

        await query.edit_message_text(
            f"📦 *Order Request*\n\n"
            f"Service: {service['name']}\n"
            f"Price: ₹{service['price']}\n\n"
            "💳 Payment system will be connected here.\n\n"
            "After payment, your order will be sent to the admin for verification.",
            parse_mode="Markdown",
        )

    elif query.data == "payment":
        await query.edit_message_text(
            "💳 *Payment*\n\n"
            "Payment gateway will be connected here.\n\n"
            "⚠️ Never send your card number, CVV or OTP to the bot.",
            parse_mode="Markdown",
        )

    elif query.data == "orders":
        await query.edit_message_text(
            "📦 *My Orders*\n\n"
            "Your orders will appear here after placing an order.",
            parse_mode="Markdown",
        )

    elif query.data == "support":
        await query.edit_message_text(
            "📞 *Support*\n\n"
            "For help with your order, contact the administrator.",
            parse_mode="Markdown",
        )

    elif query.data == "back":
        await query.edit_message_text(
            "👋 Welcome back!\n\nChoose an option from /start"
        )


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is missing!")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 GrowthMate AI Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
