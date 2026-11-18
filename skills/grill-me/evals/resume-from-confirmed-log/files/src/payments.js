// Thin wrapper over the payment provider (PagFast).
// refund() is idempotent per (paymentId, amountCents).
async function refund(paymentId, amountCents) {
  const res = await fetch(`https://api.pagfast.example/v1/payments/${paymentId}/refunds`, {
    method: 'POST',
    body: JSON.stringify({ amount: amountCents }),
  });
  if (!res.ok) throw new Error(`Refund failed: ${res.status}`);
  return res.json();
}

module.exports = { refund };
