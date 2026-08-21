import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import BOT_TOKEN
from services import SERVICES
from database import (
    init_db,
    add_user,
    create_order,
    get_user_orders,
    get_all_orders,
    get_order,
    update_order_status,
    update_payment_status,
    save_utr,
    get_all_users,
)
from admin import is_admin, admin_welcome


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# =========================
# START
# =========================

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


# =========================
# ADMIN PANEL
# =========================

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


# =========================
# ADMIN ORDERS
# =========================

async def show_admin_orders(query):
    orders = get_all_orders()

    if not orders:
        await query.edit_message_text(
            "📦 *Orders*\n\nNo orders found.",
            parse_mode="Markdown",
        )
        return

    keyboard = []

    for order in orders[:20]:
        order_id = order["id"]
        service = order["service"]
        amount = order["amount"]

        keyboard.append([
            InlineKeyboardButton(
                f"#{order_id} • ₹{amount} • {service[:20]}",
                callback_data=f"view_order_{order_id}",
            )
        ])

    keyboard.append([
        InlineKeyboardButton("⬅️ Admin Panel", callback_data="admin_home")
    ])

    await query.edit_message_text(
        "📦 *All Orders*\n\nSelect an order:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# =========================
# ADMIN ORDER DETAILS
# =========================

async def show_order_details(query, order_id):
    order = get_order(order_id)

    if not order:
        await query.edit_message_text("❌ Order not found.")
        return

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Approve Order",
                callback_data=f"approve_order_{order_id}",
            ),
            InlineKeyboardButton(
                "❌ Reject Order",
                callback_data=f"reject_order_{order_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                "⬅️ Orders",
                callback_data="admin_orders",
            )
        ],
    ]

    username = "Not available"

    text = (
        f"📦 *Order #{order['id']}*\n\n"
        f"👤 User ID: `{order['user_id']}`\n"
        f"🛍️ Service: {order['service']}\n"
        f"💰 Amount: ₹{order['amount']}\n"
        f"📊 Order Status: {order['status']}\n"
        f"💳 Payment: {order['payment_status']}\n"
        f"🔢 UTR: {order['utr'] or 'Not submitted'}\n"
        f"📅 Created: {order['created_at'][:19]}\n"
    )

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# =========================
# ADMIN PAYMENTS
# =========================

async def show_admin_payments(query):
    orders = get_all_orders()

    pending = [
        order for order in orders
        if order["payment_status"] == "Verification Pending"
    ]

    if not pending:
        await query.edit_message_text(
            "💳 *Payments*\n\n"
            "No payments are waiting for verification.",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "⬅️ Admin Panel",
                        callback_data="admin_home",
                    )
                ]
            ]),
            parse_mode="Markdown",
        )
        return

    keyboard = []

    for order in pending[:20]:
        keyboard.append([
            InlineKeyboardButton(
                f"💳 Order #{order['id']} • ₹{order['amount']}",
                callback_data=f"view_order_{order['id']}",
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "⬅️ Admin Panel",
            callback_data="admin_home",
        )
    ])

    await query.edit_message_text(
        "💳 *Pending Payments*\n\n"
        "Select a payment to verify:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# =========================
# ADMIN USERS
# =========================

async def show_admin_users(query):
    users = get_all_users()

    if not users:
        await query.edit_message_text(
            "👥 No users found."
        )
        return

    text = f"👥 *Total Users: {len(users)}*\n\n"

    for user in users[:30]:
        username = user["username"] or "No username"
        first_name = user["first_name"] or "Unknown"

        text += (
            f"👤 {first_name}\n"
            f"Username: @{username}\n"
            f"ID: `{user['user_id']}`\n\n"
        )

    keyboard = [
        [
            InlineKeyboardButton(
                "⬅️ Admin Panel",
                callback_data="admin_home",
            )
        ]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# =========================
# ADMIN HOME
# =========================

async def show_admin_home(query):
    keyboard = [
        [InlineKeyboardButton("📦 Orders", callback_data="admin_orders")],
        [InlineKeyboardButton("💳 Payments", callback_data="admin_payments")],
        [InlineKeyboardButton("👥 Users", callback_data="admin_users")],
    ]

    await query.edit_message_text(
        admin_welcome(),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =========================
# CALLBACK HANDLER
# =========================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    # =====================
    # ADMIN SECURITY
    # =====================

    if data.startswith("admin_") or data.startswith("view_order_") \
            or data.startswith("approve_order_") \
            or data.startswith("reject_order_"):

        if not is_admin(user_id):
            await query.answer(
                "⛔ Unauthorized",
                show_alert=True,
            )
            return

    # =====================
    # ADMIN HOME
    # =====================

    if data == "admin_home":
        await show_admin_home(query)
        return

    # =====================
    # ADMIN ORDERS
    # =====================

    if data == "admin_orders":
        await show_admin_orders(query)
        return

    # =====================
    # ADMIN PAYMENTS
    # =====================

    if data == "admin_payments":
        await show_admin_payments(query)
        return

    # =====================
    # ADMIN USERS
    # =====================

    if data == "admin_users":
        await show_admin_users(query)
        return

    # =====================
    # VIEW ORDER
    # =====================

    if data.startswith("view_order_"):
        order_id = int(data.replace("view_order_", ""))

        await show_order_details(
            query,
            order_id,
        )
        return

    # =====================
    # APPROVE ORDER
    # =====================

    if data.startswith("approve_order_"):
        order_id = int(data.replace("approve_order_", ""))

        order = get_order(order_id)

        if not order:
            await query.edit_message_text(
                "❌ Order not found."
            )
            return

        update_order_status(
            order_id,
            "Approved",
        )

        update_payment_status(
            order_id,
            "Paid",
        )

        try:
            await context.bot.send_message(
                chat_id=order["user_id"],
                text=(
                    f"✅ *Order Approved!*\n\n"
                    f"📦 Order ID: #{order['id']}\n"
                    f"🛍️ Service: {order['service']}\n"
                    f"💰 Amount: ₹{order['amount']}\n\n"
                    "Your payment/order has been approved by the admin."
                ),
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.error(
                "Could not notify customer: %s",
                e,
            )

        await query.edit_message_text(
            f"✅ Order #{order_id} approved successfully."
        )
        return

    # =====================
    # REJECT ORDER
    # =====================

    if data.startswith("reject_order_"):
        order_id = int(data.replace("reject_order_", ""))

        order = get_order(order_id)

        if not order:
            await query.edit_message_text(
                "❌ Order not found."
            )
            return

        update_order_status(
            order_id,
            "Rejected",
        )

        update_payment_status(
            order_id,
            "Rejected",
        )

        try:
            await context.bot.send_message(
                chat_id=order["user_id"],
                text=(
                    f"❌ *Order Rejected*\n\n"
                    f"📦 Order ID: #{order['id']}\n"
                    f"🛍️ Service: {order['service']}\n\n"
                    "Please contact support if you think this was a mistake."
                ),
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.error(
                "Could not notify customer: %s",
                e,
            )

        await query.edit_message_text(
            f"❌ Order #{order_id} rejected."
        )
        return

    # =====================
    # CUSTOMER SERVICES
    # =====================

    if data == "services":

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
        return

    # =====================
    # SERVICE DETAILS
    # =====================

    if data.startswith("service_"):

        service_id = data.replace("service_", "")
        service = SERVICES.get(service_id)

        if not service:
            await query.edit_message_text(
                "❌ Service not found."
            )
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
                    "⬅️ Back",
                    callback_data="services",
                )
            ],
        ]

        await query.edit_message_text(
            f"📌 *{service['name']}*\n\n"
            f"{service['description']}\n\n"
            f"💰 Price: ₹{service['price']}\n\n"
            "Create an order below.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )
        return

    # =====================
    # CREATE ORDER
    # =====================

    if data.startswith("buy_"):

        service_id = data.replace("buy_", "")
        service = SERVICES.get(service_id)

        if not service:
            await query.edit_message_text(
                "❌ Service not found."
            )
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
        return

    # =====================
    # MY ORDERS
    # =====================

    if data == "orders":

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
            text += (
                f"🆔 Order: #{order[0]}\n"
                f"🛍️ Service: {order[1]}\n"
                f"💰 Amount: ₹{order[2]}\n"
                f"📊 Status: {order[3]}\n"
                f"📅 Date: {order[4][:10]}\n\n"
            )

        await query.edit_message_text(
            text,
            parse_mode="Markdown",
        )
        return

    # =====================
    # PAYMENT
    # =====================

    if data == "payment":

        await query.edit_message_text(
            "💳 *Payment*\n\n"
            "Payment verification system is being prepared.\n\n"
            "⚠️ Never send your card number, CVV or OTP.",
            parse_mode="Markdown",
        )
        return

    # =====================
    # SUPPORT
    # =====================

    if data == "support":

        await query.edit_message_text(
            "📞 *Support*\n\n"
            "Please contact the administrator for help with your order.",
            parse_mode="Markdown",
        )
        return

    # =====================
    # BACK
    # =====================

    if data == "back":

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


# =========================
# ERROR HANDLER
# =========================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
):
    logger.error(
        "Exception while handling update:",
        exc_info=context.error,
    )


# =========================
# MAIN
# =========================

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

    application.add_error_handler(
        error_handler
    )

    print("🤖 GrowthMate AI Bot is running...")

    application.run_polling()


if __name__ == "__main__":
    main()
