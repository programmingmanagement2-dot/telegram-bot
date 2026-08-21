from config import ADMIN_ID


def is_admin(user_id):
    return str(user_id) == str(ADMIN_ID)


def admin_menu():
    return [
        ("📦 Orders", "admin_orders"),
        ("👥 Users", "admin_users"),
        ("💳 Payments", "admin_payments"),
    ]


def admin_welcome():
    return (
        "🔐 Admin Panel\n\n"
        "Welcome to GrowthMate AI administration panel."
    )


def order_approved_message(order_id):
    return (
        f"✅ Order #{order_id} approved.\n\n"
        "The customer can now be notified."
    )


def order_rejected_message(order_id):
    return (
        f"❌ Order #{order_id} rejected.\n\n"
        "The payment/order requires further review."
    )
    
