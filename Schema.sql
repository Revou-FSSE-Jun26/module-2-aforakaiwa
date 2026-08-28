drop table if exists order_items cascade;
drop table if exists orders cascade;
drop table if exists products cascade;
drop table if exists categories cascade;
drop table if exists users cascade;



create table users (
	user_id			SERIAL			primary key,		--auto 1,2,3, ...
	full_name 		VARCHAR(100)	not null, 			--required, max 100 chars
	email 			VARCHAR(255) 	not null unique,	--required, globally unique
	password_hash	VARCHAR(255)	not null,			--required
	is_active		BOOLEAN			default true,
	created_at		TIMESTAMP		not null default NOW() 		--auto set current time
);

create table categories (
	category_id		SERIAL			primary key,		--auto 1,2,3, ...
	category_name	VARCHAR(80)		not null unique,	--required, globally unique
	description		VARCHAR(1000),						--additional info for each category
	created_at		timestamp 		default NOW()		--auto set current time
);

create table products (
	product_id		SERIAL			primary key,
	category_id		INTEGER			not null,
	product_name	VARCHAR(255)	not null,
	sku				VARCHAR(11)		not null unique,	--Stock Keeping Unit, a unique code for identified and track specific product in storage
	description		VARCHAR(1000),						--additional info for each product
	price			numeric(12,2)	not null,
	stock_quantity	integer			not null default 0,
	is_active		boolean			not null default true,
	created_at		timestamp 		not null default now(),

	constraint fk_products_category foreign key	(category_id) references categories (category_id) on delete restrict,
	constraint chk_product_price check (price >= 0),
	constraint chk_product_stock check (stock_quantity >= 0)
);

create table orders (
	order_id			SERIAL			primary key,
	user_id				INTEGER			not null,
	order_status		VARCHAR(20)		not null default 'Pending', --("Pending", "Paid", "Shipped", "Delivered", "Canceled", "Return Process")
	shipping_address	VARCHAR(1000)	not null,
	shipping_fee		numeric(12,2)	not null default 0,
	total_amount		numeric(12,2)	not null default 0,			--Include shipping fee
	ordered_at			timestamp 		not null default NOW(),
	
	constraint fk_orders_user foreign key (user_id) references users (user_id) on delete restrict, --keep order history
	constraint chk_orders_status check (order_status in ('Pending', 'Paid', 'Shipped', 'Delivered', 'Cancelled', 'Return Process')),
	constraint chk_orders_totals check (shipping_fee >= 0 and total_amount >= 0)
);

create table order_items (
	order_item_id		SERIAL			primary key,
	order_id			INTEGER			not null,
	product_id			INTEGER			not null,
	quantity			INTEGER			not null,
	unit_price			numeric(12,2)	not null,
	line_total			numeric(12,2),	
	
	constraint fk_order_id foreign key (order_id) references orders (order_id) on delete cascade, 
	constraint fk_order_items_product foreign key (product_id) references products (product_id) on delete restrict, --cannot delete product that has been sold
	constraint chk_order_items_quantity check (quantity > 0),
	constraint chk_order_items_unit_price check (unit_price >= 0)
);