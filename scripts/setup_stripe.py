"""
Run this once to create Stripe products and prices for ThreatPulse.
Requires: pip install stripe
Usage: STRIPE_SECRET_KEY=sk_test_xxx python scripts/setup_stripe.py
"""
import os
import stripe

stripe.api_key = os.environ["STRIPE_SECRET_KEY"]

print("Creating ThreatPulse Stripe products...\n")

# Professional Plan
pro_product = stripe.Product.create(
    name="ThreatPulse Professional",
    description="Full threat profiles, IOCs, remediation playbooks, AI advisor, real-time alerts",
)
pro_price = stripe.Price.create(
    product=pro_product.id,
    unit_amount=3900,
    currency="usd",
    recurring={"interval": "month"},
)
print(f"Professional Product: {pro_product.id}")
print(f"Professional Price:   {pro_price.id}  ($39/month)")
print()

# Enterprise Plan
ent_product = stripe.Product.create(
    name="ThreatPulse Enterprise",
    description="API access, SIEM integration, custom reports, priority alerting, 25 team seats",
)
ent_price = stripe.Price.create(
    product=ent_product.id,
    unit_amount=19900,
    currency="usd",
    recurring={"interval": "month"},
)
print(f"Enterprise Product:   {ent_product.id}")
print(f"Enterprise Price:     {ent_price.id}  ($199/month)")
print()

print("Add these to your .env file:")
print(f"STRIPE_PRICE_PRO={pro_price.id}")
print(f"STRIPE_PRICE_ENTERPRISE={ent_price.id}")
print()

# Create Customer Portal configuration
portal = stripe.billing_portal.Configuration.create(
    business_profile={"headline": "ThreatPulse Subscription Management"},
    features={
        "subscription_cancel": {"enabled": True, "mode": "at_period_end"},
        "subscription_update": {
            "enabled": True,
            "default_allowed_updates": ["price"],
            "products": [
                {"product": pro_product.id, "prices": [pro_price.id]},
                {"product": ent_product.id, "prices": [ent_price.id]},
            ],
        },
        "invoice_history": {"enabled": True},
    },
)
print(f"Customer Portal Config: {portal.id}")
print("\nDone. Stripe is ready.")
