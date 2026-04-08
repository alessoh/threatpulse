import stripe
from app.core.config import get_settings
from app.models.user import User
from sqlalchemy.orm import Session


def get_stripe():
    settings = get_settings()
    stripe.api_key = settings.stripe_secret_key
    return stripe


def create_checkout_session(user: User, price_id: str, success_url: str, cancel_url: str) -> str:
    s = get_stripe()

    if not user.stripe_customer_id:
        customer = s.Customer.create(email=user.email, name=user.full_name)
        user.stripe_customer_id = customer.id

    session = s.checkout.Session.create(
        customer=user.stripe_customer_id,
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="subscription",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"user_id": str(user.id)},
    )

    return session.url


def create_portal_session(customer_id: str, return_url: str) -> str:
    s = get_stripe()
    session = s.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )
    return session.url


def handle_webhook_event(payload: bytes, sig_header: str, db: Session):
    settings = get_settings()
    s = get_stripe()

    event = s.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)
    data = event.data.object

    if event.type == "checkout.session.completed":
        user_id = data.metadata.get("user_id")
        if user_id:
            user = db.query(User).filter(User.id == int(user_id)).first()
            if user:
                user.stripe_subscription_id = data.subscription
                sub = s.Subscription.retrieve(data.subscription)
                price_id = sub.items.data[0].price.id
                if price_id == settings.stripe_price_enterprise:
                    user.tier = "enterprise"
                else:
                    user.tier = "pro"
                db.commit()

    elif event.type == "customer.subscription.updated":
        sub_id = data.id
        user = db.query(User).filter(User.stripe_subscription_id == sub_id).first()
        if user:
            if data.status == "active":
                price_id = data.items.data[0].price.id
                if price_id == settings.stripe_price_enterprise:
                    user.tier = "enterprise"
                else:
                    user.tier = "pro"
            elif data.status in ("canceled", "unpaid", "past_due"):
                user.tier = "free"
            db.commit()

    elif event.type == "customer.subscription.deleted":
        sub_id = data.id
        user = db.query(User).filter(User.stripe_subscription_id == sub_id).first()
        if user:
            user.tier = "free"
            user.stripe_subscription_id = None
            db.commit()

    return {"status": "ok"}
