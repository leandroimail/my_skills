const { notifyQueue } = require('./queue');

const orders = new Map();

function getOrder(id) {
  const order = orders.get(id);
  if (!order) throw new Error('Order not found');
  return order;
}

// Cancels the whole order. There is no item-level cancellation.
function cancelOrder(id) {
  const order = getOrder(id);
  if (order.status === 'shipped') throw new Error('Cannot cancel a shipped order');
  order.status = 'cancelled';
  notifyQueue.push({ type: 'order_cancelled', orderId: id });
  return order;
}

module.exports = { getOrder, cancelOrder, orders };
