from config import ADMIN_ID


def create_payment_request(user_id, order_id, amount):
    """
    Creates a payment request.
    Actual payment gateway can be connected later.
    """

    return {
        "user_id": user_id,
        "order_id": order_id,
        "amount": amount,
        "status": "Pending Payment",
    }


def verify_payment(payment_reference):
    """
    Payment verification placeholder.

    Later we can connect an official payment gateway/API
    for automatic verification.
    """

    if not payment_reference:
        return False

    return True


def admin_payment_message(order_id, user_id, amount, payment_reference):
    return (
        "💳 PAYMENT VERIFICATION\n\n"
        f"📦 Order ID: {order_id}\n"
        f"👤 User ID: {user_id}\n"
        f"💰 Amount: ₹{amount}\n"
        f"🧾 Reference: {payment_reference}\n\n"
        "Please verify the payment before approving the order."
    )
