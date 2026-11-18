# 1. Customer notifications are always asynchronous

Status: accepted

E-mail delivery through our provider takes 2 to 8 seconds and fails about 1% of the time. Sending inside the request made checkout and cancellation time out. All customer notifications go through `notifyQueue` and are sent by the worker. Request handlers never call the e-mail provider directly.
