-- users (8 accounts, one deactivated)
insert into users (full_name, email, password_hash, is_active, created_at) values
('Andi Pratama',      'andi.pratama@gmail.com',        'Password#Hash1', true,  '2025-11-03 09:12:00+07'),
('Siti Nurhaliza',    'siti.nurhaliza@yahoo.com',      'Password#Hash2', true,  '2025-12-14 18:40:00+07'),
('Budi Santoso',      'budi.santoso@outlook.com',      'Password#Hash3', true,  '2026-01-08 07:55:00+07'),
('Rina Wijaya',       'rina.wijaya@gmail.com',         'Password#Hash4', true,  '2026-01-22 13:05:00+07'),
('Kevin Tanuwijaya',  'kevin.tan@revoshop.dev',        'Password#Hash5', true,  '2026-02-11 20:31:00+07'),
('Dewi Lestari',      'dewi.lestari@gmail.com',        'Password#Hash6', true,  '2026-03-02 11:17:00+07'),
('Fajar Ramadhan',    'fajar.ramadhan@proton.me',      'Password#Hash7', true,  '2026-04-19 16:48:00+07'),
('Maria Simanjuntak', 'maria.simanjuntak@gmail.com',   'Password#Hash8', false, '2026-05-27 08:03:00+07');

-- categories (6)
insert into categories (category_name, description) values
('Electronics',          'Gadgets, computer peripherals and audio gear.'),
('Fashion',              'Clothing, footwear and everyday bags.'),
('Home & Living',        'Furniture, kitchenware and home lighting.'),
('Books & Stationery',   'Printed books, notebooks and writing tools.'),
('Sports & Outdoors',    'Fitness equipment and outdoor accessories.'),
('Health & Beauty',      'Skincare, personal care and daily essentials.');

-- products (23, spread across all 6 categories)
-- Includes one out-of-stock item and one discontinued item.
insert into products (category_id, product_name, sku, description, price, stock_quantity, is_active) values
-- Electronics
(1, 'Logitech MX Master 3S Wireless Mouse', 'ELC-MOU-001', 'Ergonomic 8K DPI mouse with quiet clicks and USB-C charging.',        1450000.00,  42, TRUE),
(1, 'Anker PowerCore 20000mAh Power Bank',  'ELC-PWB-002', '20000mAh power bank with 30W USB-C Power Delivery.',                   549000.00, 130, TRUE),
(1, 'Samsung 27" 4K UHD Monitor UR55',      'ELC-MON-003', '27-inch 3840x2160 IPS monitor with HDR10 and FreeSync.',              3899000.00,  15, TRUE),
(1, 'Keychron K2 Mechanical Keyboard',      'ELC-KEY-004', '75% hot-swappable wireless keyboard, brown switches.',                1299000.00,  25, TRUE),
(1, 'Sony WH-1000XM5 Headphones',           'ELC-HDP-005', 'Over-ear noise cancelling headphones, 30-hour battery.',              4999000.00,   8, TRUE),
-- Fashion
(2, 'Uniqlo AIRism Cotton T-Shirt',         'FSH-TSH-006', 'Breathable crew-neck tee, unisex sizing S-XXL.',                       199000.00, 200, TRUE),
(2, 'Levi''s 511 Slim Fit Jeans',           'FSH-JNS-007', 'Stretch denim slim fit jeans, dark indigo wash.',                      899000.00,  60, TRUE),
(2, 'Eiger Canvas Daypack 25L',             'FSH-BAG-008', 'Water-resistant canvas backpack with padded laptop sleeve.',           675000.00,  35, TRUE),
(2, 'Adidas Runfalcon 3.0 Sneakers',        'FSH-SHO-009', 'Lightweight running shoes with Cloudfoam midsole.',                    799000.00,  48, TRUE),
-- Home & Living
(3, 'IKEA MARKUS Office Chair',             'HML-CHR-010', 'High-back mesh office chair with tilt lock, 10-year warranty.',       2799000.00,  12, TRUE),
(3, 'Ceramic Coffee Mug Set (4 pcs)',       'HML-MUG-011', 'Matte glazed 350ml stoneware mugs, dishwasher safe.',                  165000.00,  90, TRUE),
(3, 'Philips LED Desk Lamp',                'HML-LMP-012', 'Dimmable desk lamp with 3 colour temperatures and USB port.',          349000.00,  55, TRUE),
(3, 'Non-stick Frying Pan 24cm',            'HML-PAN-013', 'Induction-ready aluminium pan with granite coating.',                  259000.00,  70, TRUE),
-- Books & Stationery
(4, 'Clean Code - Robert C. Martin',        'BKS-BOK-014', 'A handbook of agile software craftsmanship, paperback.',               585000.00,  20, TRUE),
(4, 'Designing Data-Intensive Applications','BKS-BOK-015', 'Martin Kleppmann''s guide to reliable, scalable systems.',             725000.00,  14, TRUE),
(4, 'Pilot G2 Gel Pen (Box of 12)',         'BKS-PEN-016', '0.7mm retractable gel pens, black ink.',                               132000.00, 150, TRUE),
(4, 'A5 Hardcover Dotted Notebook',         'BKS-NTB-017', '160 pages, 100gsm dotted paper with elastic band.',                     89000.00, 110, TRUE),
-- Sports & Outdoors
(5, 'Yoga Mat TPE 6mm',                     'SPT-YGM-018', 'Non-slip double-layer TPE mat with carrying strap.',                   245000.00,  65, TRUE),
(5, 'Adjustable Dumbbell 10kg',             'SPT-DMB-019', 'Single dumbbell with removable plates, rubber coated.',                615000.00,  22, TRUE),
(5, 'Stainless Steel Water Bottle 1L',      'SPT-BTL-020', 'Double-wall vacuum insulated bottle, keeps cold 24h.',                 175000.00,  95, TRUE),
-- Health & Beauty
(6, 'Wardah UV Shield Sunscreen SPF 35',    'HBT-SUN-021', 'Lightweight daily sunscreen for face, 40ml.',                           45000.00, 180, TRUE),
(6, 'Sensodyne Repair & Protect 100g',      'HBT-TPT-022', 'Toothpaste for sensitive teeth - currently out of stock.',              32000.00,   0, TRUE),
(6, 'Somethinc Niacinamide 10% Serum',      'HBT-SRM-023', 'Discontinued formulation, kept for order history only.',               149000.00,  40, FALSE);

-- orders (12, across 7 users and every status)
-- total_amount is left at 0 here and recalculated at the end of
-- this script from the actual order_items rows.
insert into orders (user_id, order_status, shipping_address, shipping_fee, ordered_at) values
(1, 'Delivered', 'Jl. Margonda Raya No. 45, Beji, Depok, Jawa Barat 16424',           22000.00, '2026-02-04 10:22:00+07'),
(2, 'Delivered', 'Jl. Dipatiukur No. 112, Coblong, Bandung, Jawa Barat 40132',        28000.00, '2026-02-17 15:47:00+07'),
(3, 'Shipped',   'Jl. Senopati No. 8, Kebayoran Baru, Jakarta Selatan 12190',         18000.00, '2026-03-09 09:05:00+07'),
(1, 'Delivered', 'Jl. Margonda Raya No. 45, Beji, Depok, Jawa Barat 16424',           22000.00, '2026-03-21 19:33:00+07'),
(4, 'Cancelled', 'Jl. Raya Darmo No. 77, Wonokromo, Surabaya, Jawa Timur 60241',      35000.00, '2026-04-02 08:14:00+07'),
(5, 'Paid',      'Jl. Boulevard Gading Serpong Blok M2/9, Tangerang, Banten 15810',   20000.00, '2026-04-15 21:08:00+07'),
(6, 'Delivered', 'Jl. Kaliurang KM 5 No. 21, Sleman, Yogyakarta 55281',               30000.00, '2026-05-06 12:41:00+07'),
(3, 'Delivered', 'Jl. Senopati No. 8, Kebayoran Baru, Jakarta Selatan 12190',         18000.00, '2026-05-19 17:26:00+07'),
(7, 'Pending',   'Jl. Akses UI No. 130, Tugu, Depok, Jawa Barat 16451',               22000.00, '2026-06-11 11:59:00+07'),
(2, 'Shipped',   'Jl. Dipatiukur No. 112, Coblong, Bandung, Jawa Barat 40132',        28000.00, '2026-06-28 14:10:00+07'),
(5, 'Delivered', 'Jl. Boulevard Gading Serpong Blok M2/9, Tangerang, Banten 15810',   20000.00, '2026-07-09 09:47:00+07'),
(6, 'Paid',      'Jl. Kaliurang KM 5 No. 21, Sleman, Yogyakarta 55281',               30000.00, '2026-07-24 20:02:00+07');


-- order_items (30 line items - the many-to-many junction rows)
-- unit_price is the price captured at purchase time, which is why
-- a few rows differ from the current products.price (promo pricing).
insert into order_items (order_id, product_id, quantity, unit_price) values
-- Order 1 - Andi: work-from-home setup
(1,  1, 1, 1450000.00),
(1,  4, 1, 1199000.00),   -- launch promo price
(1, 12, 2,  349000.00),
-- Order 2 - Siti: wardrobe refresh
(2,  6, 3,  199000.00),
(2,  9, 1,  799000.00),
(2, 20, 1,  175000.00),
-- Order 3 - Budi: reading list
(3, 14, 1,  585000.00),
(3, 15, 1,  725000.00),
(3, 17, 2,   89000.00),
-- Order 4 - Andi: kitchen restock
(4, 11, 1,  165000.00),
(4, 13, 1,  259000.00),
(4, 21, 3,   45000.00),
-- Order 5 - Rina: cancelled big-ticket order
(5,  5, 1, 4999000.00),
(5,  3, 1, 3899000.00),
-- Order 6 - Kevin: home gym
(6, 18, 1,  245000.00),
(6, 19, 2,  615000.00),
(6, 20, 2,  175000.00),
-- Order 7 - Dewi: desk upgrade
(7, 10, 1, 2799000.00),
(7, 16, 1,  132000.00),
(7, 17, 3,   89000.00),
-- Order 8 - Budi: audio + power
(8,  5, 1, 4749000.00),   -- flash sale price
(8,  2, 1,  549000.00),
-- Order 9 - Fajar: pending checkout
(9,  6, 2,  199000.00),
(9,  8, 1,  675000.00),
-- Order 10 - Siti: gifts
(10, 11, 2,  165000.00),
(10, 23, 1,  149000.00),  -- product later discontinued, history preserved
-- Order 11 - Kevin: peripherals
(11,  1, 2, 1450000.00),
(11,  4, 1, 1299000.00),
-- Order 12 - Dewi: everyday items
(12, 21, 4,   45000.00),
(12, 22, 2,   32000.00);

-- Recalculate every order_item with qty * unit_price
update order_items set line_total = quantity * unit_price;


-- Recalculate every order total from its line items + shipping fee
-- so orders.total_amount is always consistent with order_items.
update orders o
set total_amount = o.shipping_fee + COALESCE((
        select SUM(oi.line_total)
        from order_items oi
        where oi.order_id = o.order_id
    ), 0);