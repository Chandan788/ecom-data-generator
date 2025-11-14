-- Report: Customer orders with line item and payment details
SELECT
    c.name AS customer_name,
    o.order_id,
    o.order_date,
    pdt.name AS product_name,
    pdt.category,
    oi.quantity,
    pdt.price,
    (oi.quantity * pdt.price) AS total_item_amount,
    pay.mode AS payment_mode
FROM customers AS c
JOIN orders AS o ON o.customer_id = c.customer_id
JOIN payments AS pay ON pay.order_id = o.order_id
JOIN order_items AS oi ON oi.order_id = o.order_id
JOIN products AS pdt ON pdt.product_id = oi.product_id
WHERE pay.amount > 0
ORDER BY o.order_date DESC;
