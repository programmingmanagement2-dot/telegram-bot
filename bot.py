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
from database import init_db, add_user, create_order, get_user_orders
from admin import is_admin, admin_welcome


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    add_user(
        user.id,
        user.username,
        user.first_name,
    )

    keyboard = [
        [InlineKeyboardButton("🛍️ Services", callback_data="services")],
        [InlineKeyboardButton("📦 My Orders", callback_data="orders")],
        [InlineKeyboardButton("💳 Payment", callback_data="payment")],
        [InlineKeyboardButton("📞 Support", callback_data="support")],
    ]

    await update.message.reply_text(
        "👋 Welcome to *GrowthMate AI*!\n\n"
        "🚀 Digital Growth & Development Services\n\n"
        "Choose an option below:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text(
            "⛔ Access denied.\n\n"
            "You are not authorized to use the Admin Panel."
        )
        return

    keyboard = [
        [InlineKeyboardButton("📦 Orders", callback_data="admin_orders")],
        [InlineKeyboardButton("💳 Payments", callback_data="admin_payments")],
        [InlineKeyboardButton("👥 Users", callback_data="admin_users")],
    ]

    await update.message.reply_text(
        admin_welcome(),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "services":

        keyboard = []

        for service_id, service in SERVICES.items():
            keyboard.append([
                InlineKeyboardButton(
                    service["name"],
                    callback_data=f"service_{service_id}",
                )
            ])

        keyboard.append([
            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="back",
            )
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
            [
                InlineKeyboardButton(
                    "🛒 Create Order",
                    callback_data=f"buy_{service_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    "⬅️ Back to Services",
                    callback_data="services",
                )
            ],
        ]

        await query.edit_message_text(
            f"📌 *{service['name']}*\n\n"
            f"{service['description']}\n\n"
            f"💰 Starting Price: ₹{service['price']}\n\n"
            "Tap below to create an order.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

    elif query.data.startswith("buy_"):

        service_id = query.data.replace("buy_", "")
        service = SERVICES.get(service_id)

        if not service:
            await query.edit_message_text("❌ Service not found.")
            return

        order_id = create_order(
            user_id=user_id,
            service=service["name"],
            amount=service["price"],
        )

        await query.edit_message_text(
            f"✅ *Order Created!*\n\n"
            f"📦 Order ID: #{order_id}\n"
            f"🛍️ Service: {service['name']}\n"
            f"💰 Amount: ₹{service['price']}\n\n"
            "💳 Payment verification will be connected next.\n\n"
            "Please keep your Order ID safe.",
            parse_mode="Markdown",
        )

    elif query.data == "orders":

        orders = get_user_orders(user_id)

        if not orders:
            await query.edit_message_text(
                "📦 *My Orders*\n\n"
                "You don't have any orders yet.",
                parse_mode="Markdown",
            )
            return

        text = "📦 *Your Orders*\n\n"

        for order in orders:
            order_id, service, amount, status, created_at = order

            text += (
                f"🆔 Order: #{order_id}\n"
                f"🛍️ Service: {service}\n"
                f"💰 Amount: ₹{amount}\n"
                f"📊 Status: {status}\n"
                f"📅 Date: {created_at[:10]}\n\n"
            )

        await query.edit_message_text(
            text,
            parse_mode="Markdown",
        )

    elif query.data == "payment":

        await query.edit_message_text(
            "💳 *Payment*\n\n"
            "Payment system will be connected next.\n\n"
            "⚠️ Never send your card number, CVV or OTP to the bot.",
            parse_mode="Markdown",
        )

    elif query.data == "support":

        await query.edit_message_text(
            "📞 *Support*\n\n"
            "For order-related help, contact the administrator.",
            parse_mode="Markdown",
        )

    elif query.data == "back":

        keyboard = [
            [
                InlineKeyboardButton(
                    "🛍️ Services",
                    callback_data="services",
                )
            ],
            [
                InlineKeyboardButton(
                    "📦 My Orders",
                    callback_data="orders",
                )
            ],
        ]

        await query.edit_message_text(
            "🏠 *Main Menu*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

    elif query.data.startswith("admin_"):

        if not is_admin(user_id):
            await query.answer(
                "⛔ Unauthorized",
                show_alert=True,
            )
            return

        await query.edit_message_text(
            "🚧 This Admin section will be connected next."
        )


async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
):
    logger.error(
        "Exception while handling update:",
        exc_info=context.error,
    )


def main():

    if not BOT_TOKEN:
        raise ValueError(
            "BOT_TOKEN is missing. "
            "Set it as an environment variable."
        )

    init_db()

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("admin", admin_command)
    )

    application.add_handler(
        CallbackQueryHandler(button_handler)
    )

    application.add_error_handler(error_handler)

    print("🤖 GrowthMate AI Bot is running...")

    application.run_polling()


if __name__ == "__main__":
    main()
