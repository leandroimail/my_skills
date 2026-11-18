"""Order pricing rules."""

TIER_RATES = {"standard": 0.0, "silver": 0.05, "gold": 0.10}
VOLUME_THRESHOLD = 1000.0
VOLUME_BONUS = 0.05
COUPON_BONUS = 0.10
MAX_RATE = 0.20


def apply_discount(subtotal: float, customer_tier: str, coupon: str | None = None) -> float:
    """Return the amount to charge after tier, volume and coupon discounts."""
    if subtotal < 0:
        raise ValueError("subtotal must not be negative")
    if customer_tier not in TIER_RATES:
        raise ValueError(f"unknown customer tier: {customer_tier}")
    rate = TIER_RATES[customer_tier]
    if subtotal >= VOLUME_THRESHOLD:
        rate += VOLUME_BONUS
    if coupon == "WELCOME10":
        rate += COUPON_BONUS
    rate = min(rate, MAX_RATE)
    return round(subtotal * (1 - rate), 2)
