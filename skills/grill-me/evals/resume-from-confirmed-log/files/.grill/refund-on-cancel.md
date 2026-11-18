# Grill: automatic refund when an order is cancelled
Date: 2026-11-10
Mode: interview
Confirmed: 2026-11-10

## Intent
When a customer cancels an order, the money goes back without anyone on the support team having to act.

## Constraints
- Customer notifications stay asynchronous (ADR 0001).

## Key decisions
- Decision: refund only whole orders in this delivery. Reason: the code has no item-level cancellation. Rejected: implementing partial cancellation now. Source: src/orders.js.
- Decision: the order is cancelled first; a failed refund is recorded and retried, the cancellation is not rolled back. Reason: cancelling is the customer's intent and must not depend on the payment provider. Rejected: failing the cancellation when the refund fails.
- Decision: the confirmation e-mail goes through notifyQueue. Reason: ADR 0001. Rejected: sending it inside the request.

## My calls (unconfirmed)
- Store `refundStatus` (pending | done | failed) on the order object. Reason: simplest place to resume from. Added 2026-11-11, after the confirmation.
- Retry a failed refund at most 3 times. Reason: refund() is idempotent, so retries are safe. Added 2026-11-11, after the confirmation.

## Out of scope
- Item-level (partial) cancellation.
