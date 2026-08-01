-- "The 5 most expensive in-stock Electronics products."
select
    p.product_id,
    p.product_name,
    p.sku,
    p.price,
    p.stock_quantity
from products p
where p.category_id = 1          -- Electronics
  and p.is_active  = true
  and p.stock_quantity > 0
order by p.price desc
limit 5;

-- Same three clauses, different shape: the 3 most recent orders that have not been delivered yet.
select
    o.order_id,
    u.full_name,
    o.order_status,
    o.total_amount,
    o.ordered_at
from orders o
left join users u on u.user_id = o.user_id
	where o.order_status in ('Pending', 'Paid', 'Shipped')
order by o.ordered_at desc
limit 3;

-- Products with their category name (products -> categories).
select
    p.product_name,
    c.category_name,
    p.price,
    p.stock_quantity
from products p
inner join categories c on c.category_id = p.category_id
order by c.category_name, p.product_name;

-- Full order detail
select
    o.order_id,
    u.full_name,
    o.order_status,
    p.product_name,
    oi.quantity,
    oi.unit_price,
    oi.line_total
from order_items oi
inner join orders o on o.order_id   = oi.order_id
inner join users u on u.user_id    = o.user_id
inner join products p on p.product_id = oi.product_id
--where o.order_id = 1
order by oi.order_item_id;

-- Best sellers: total units sold per product, excluding cancelled orders. Top 5 only.
select
    p.product_name,
    SUM(oi.quantity)   as units_sold,
    SUM(oi.line_total) as revenue
from order_items oi
inner join products p on p.product_id = oi.product_id
inner join orders o on o.order_id   = oi.order_id
where o.order_status != 'Cancelled'
group by p.product_id, p.product_name
order by units_sold desc, revenue desc
limit 5;