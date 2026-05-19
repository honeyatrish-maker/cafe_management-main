from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import mysql.connector
from mysql.connector import Error
import sqlite3
from functools import wraps
import json
import os
from urllib.parse import urlparse, unquote

app = Flask(__name__)
# Use environment variable for secret key in production
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key_here')

INSTANCE_DIR = os.path.join(os.path.dirname(__file__), 'instance')
SQLITE_DB_PATH = os.path.join(INSTANCE_DIR, 'cafe_management.db')


def get_env_var(*names, default=None):
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return default


def parse_database_url(url):
    if not url:
        return {}

    parsed = urlparse(url)
    if parsed.scheme not in (
        'mysql', 'mysql+mysqlconnector', 'mysql+mysql', 'mysql2', 'mysql+pymysql', 'mysql+mysqldb'
    ):
        return {}

    db_name = parsed.path.lstrip('/') if parsed.path else None
    return {
        'host': parsed.hostname,
        'user': unquote(parsed.username) if parsed.username else None,
        'password': unquote(parsed.password) if parsed.password else None,
        'database': db_name,
        'port': parsed.port or 3306
    }


def build_db_config():
    config = parse_database_url(
        get_env_var(
            'DB_URL', 'DATABASE_URL', 'MYSQL_DATABASE_URL', 'CLEARDB_DATABASE_URL', 'RENDER_DATABASE_URL'
        )
    )

    config['host'] = config.get('host') or get_env_var(
        'DB_HOST', 'MYSQL_HOST', 'MYSQL_HOSTNAME', 'DB_SERVER', 'MYSQL_SERVER', 'HOST'
    )
    config['user'] = config.get('user') or get_env_var(
        'DB_USER', 'MYSQL_USER', 'DB_USERNAME', 'MYSQL_USERNAME', 'USER'
    )
    config['password'] = config.get('password') or get_env_var(
        'DB_PASSWORD', 'MYSQL_PASSWORD', 'PASSWORD'
    )
    config['database'] = config.get('database') or get_env_var(
        'DB_NAME', 'MYSQL_DATABASE', 'DATABASE', 'SCHEMA'
    )
    config['port'] = int(get_env_var('DB_PORT', 'MYSQL_PORT', 'PORT', default=str(config.get('port', 3306))))

    app.logger.info(
        "DB config detection: host=%s user=%s database=%s port=%s",
        bool(config.get('host')),
        bool(config.get('user')),
        bool(config.get('database')),
        config.get('port')
    )

    return config


class SQLiteCursor(sqlite3.Cursor):
    def execute(self, sql, params=()):
        return super().execute(sql.replace('%s', '?'), params)

    def executemany(self, sql, seq_of_params):
        return super().executemany(sql.replace('%s', '?'), seq_of_params)


class SQLiteConnection(sqlite3.Connection):
    def cursor(self, factory=SQLiteCursor, *args, **kwargs):
        kwargs.pop('dictionary', None)
        return super().cursor(factory, *args, **kwargs)


def build_sqlite_connection():
    os.makedirs(INSTANCE_DIR, exist_ok=True)
    conn = sqlite3.connect(SQLITE_DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES, factory=SQLiteConnection)
    conn.row_factory = sqlite3.Row
    ensure_sqlite_schema(conn)
    return conn


def ensure_sqlite_schema(conn):
    cursor = conn.cursor()
    cursor.execute('PRAGMA foreign_keys = ON')
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if cursor.fetchone():
        return

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'admin',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT,
            available INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS tables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_number INTEGER UNIQUE NOT NULL,
            capacity INTEGER DEFAULT 4,
            status TEXT DEFAULT 'available'
        );

        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            table_id INTEGER,
            order_time TEXT DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending',
            total_amount REAL DEFAULT 0,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (table_id) REFERENCES tables(id)
        );

        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            menu_item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
        );

        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment_method TEXT DEFAULT 'cash',
            payment_time TEXT DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (order_id) REFERENCES orders(id)
        );
    ''')
    insert_sqlite_sample_data(conn)
    conn.commit()


def insert_sqlite_sample_data(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM users")
    if cursor.fetchone()['count'] == 0:
        cursor.execute(
            'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
            ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6fMJyUq7K6', 'admin')
        )

    cursor.execute("SELECT COUNT(*) as count FROM menu_items")
    if cursor.fetchone()['count'] == 0:
        menu_items = [
            ('Espresso', 'Strong coffee shot', 3.50, 'Beverages'),
            ('Cappuccino', 'Coffee with steamed milk and foam', 4.50, 'Beverages'),
            ('Latte', 'Coffee with steamed milk', 4.00, 'Beverages'),
            ('Americano', 'Diluted espresso', 3.00, 'Beverages'),
            ('Croissant', 'Buttery pastry', 2.50, 'Bakery'),
            ('Muffin', 'Fresh baked muffin', 3.00, 'Bakery'),
            ('Sandwich', 'Ham and cheese sandwich', 6.50, 'Food'),
            ('Salad', 'Fresh garden salad', 7.00, 'Food'),
            ('Pasta', 'Creamy pasta dish', 8.50, 'Food'),
            ('Burger', 'Classic beef burger', 9.00, 'Food')
        ]
        cursor.executemany(
            'INSERT INTO menu_items (name, description, price, category) VALUES (?, ?, ?, ?)',
            menu_items
        )

    cursor.execute("SELECT COUNT(*) as count FROM tables")
    if cursor.fetchone()['count'] == 0:
        cursor.executemany(
            'INSERT INTO tables (table_number, capacity) VALUES (?, ?)',
            [(1, 2), (2, 4), (3, 6), (4, 2), (5, 4), (6, 8)]
        )

    cursor.execute("SELECT COUNT(*) as count FROM customers")
    if cursor.fetchone()['count'] == 0:
        customers = [
            ('John Doe', '123-456-7890', 'john@example.com'),
            ('Jane Smith', '098-765-4321', 'jane@example.com')
        ]
        cursor.executemany(
            'INSERT INTO customers (name, phone, email) VALUES (?, ?, ?)',
            customers
        )

    conn.commit()


DB_CONFIG = build_db_config()
USE_MYSQL = bool(DB_CONFIG['host'] and DB_CONFIG['user'] and DB_CONFIG['password'] and DB_CONFIG['database'])

# Database configuration (use environment variables on Render)

# Session configuration
app.config['SESSION_TYPE'] = 'filesystem'


def get_db_connection():
    if USE_MYSQL:
        missing = [key for key in ('host', 'user', 'password', 'database') if not DB_CONFIG.get(key)]
        if missing:
            app.logger.warning('Incomplete MySQL configuration, falling back to SQLite: %s', missing)
            return build_sqlite_connection()
        try:
            return mysql.connector.connect(**DB_CONFIG)
        except Error as err:
            app.logger.error('Database connection failed: %s', err)
            app.logger.warning('Falling back to SQLite due to MySQL connection failure')
            return build_sqlite_connection()

    return build_sqlite_connection()


@app.errorhandler(404)
def handle_not_found(error):
    app.logger.warning('Page not found: %s', request.path)
    return render_template('error.html', message='Page not found. Please return to the home page.'), 404


@app.errorhandler(Exception)
def handle_exception(error):
    app.logger.exception('Unhandled exception during request')
    if isinstance(error, RuntimeError):
        message = str(error)
    else:
        message = 'The server encountered an internal error and was unable to complete your request.'
    return render_template('error.html', message=message), 500


def init_admin_user():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT id, password FROM users WHERE username = %s', ('admin',))
        user = cursor.fetchone()

        if not user:
            password_hash = generate_password_hash('admin123')
            cursor.execute('INSERT INTO users (username, password, role) VALUES (%s, %s, %s)',
                           ('admin', password_hash, 'admin'))
            conn.commit()
        elif user['password'].startswith('$2b$'):
            password_hash = generate_password_hash('admin123')
            cursor.execute('UPDATE users SET password = %s WHERE id = %s',
                           (password_hash, user['id']))
            conn.commit()

        cursor.close()
        conn.close()
    except Error as err:
        print('Admin user initialization failed:', err)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get menu items
    cursor.execute('SELECT * FROM menu_items WHERE available = TRUE ORDER BY category, name')
    menu_items = cursor.fetchall()

    # Get categories
    cursor.execute('SELECT DISTINCT category FROM menu_items WHERE available = TRUE ORDER BY category')
    categories_result = cursor.fetchall()
    categories = [row['category'] for row in categories_result]

    # Get available tables
    cursor.execute('SELECT * FROM `tables` WHERE status = %s', ('available',))
    tables = cursor.fetchall()

    # Get menu count
    cursor.execute('SELECT COUNT(*) as count FROM menu_items WHERE available = TRUE')
    menu_count = cursor.fetchone()['count']

    # Get available tables count
    available_tables_count = len(tables)

    cursor.close()
    conn.close()

    return render_template('index.html',
                         menu_items=menu_items,
                         categories=categories,
                         tables=tables,
                         menu_count=menu_count,
                         available_tables=available_tables_count)

@app.route('/admin')
def admin():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('admin_login'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('Please enter both username and password', 'error')
            return redirect(url_for('admin_login'))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user'] = user['username']
            session['role'] = user['role']
            flash(f'Welcome back, {user["username"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get today's orders count
    cursor.execute("SELECT COUNT(*) as count FROM orders WHERE DATE(order_time) = CURDATE()")
    today_orders = cursor.fetchone()['count']

    # Get today's revenue
    cursor.execute("SELECT SUM(total_amount) as revenue FROM orders WHERE DATE(order_time) = CURDATE() AND status != 'cancelled'")
    today_revenue = cursor.fetchone()['revenue'] or 0

    # Get total menu items
    cursor.execute("SELECT COUNT(*) as count FROM menu_items WHERE available = TRUE")
    menu_count = cursor.fetchone()['count']

    # Get pending orders
    cursor.execute("SELECT COUNT(*) as count FROM orders WHERE status IN ('pending', 'preparing')")
    pending_orders = cursor.fetchone()['count']

    cursor.close()
    conn.close()

    stats = {
        'today_orders': today_orders,
        'today_revenue': round(today_revenue, 2),
        'menu_count': menu_count,
        'pending_orders': pending_orders
    }

    return render_template('dashboard.html', stats=stats)

@app.route('/menu', methods=['GET', 'POST'])
@login_required
def menu():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        if 'add_item' in request.form:
            name = request.form['name']
            description = request.form['description']
            price = float(request.form['price'])
            category = request.form['category']

            cursor.execute('INSERT INTO menu_items (name, description, price, category) VALUES (%s, %s, %s, %s)',
                         (name, description, price, category))
            conn.commit()
            flash('Menu item added successfully', 'success')

        elif 'edit_item' in request.form:
            item_id = request.form['item_id']
            name = request.form['name']
            description = request.form['description']
            price = float(request.form['price'])
            category = request.form['category']
            available = 'available' in request.form

            cursor.execute('UPDATE menu_items SET name=%s, description=%s, price=%s, category=%s, available=%s WHERE id=%s',
                         (name, description, price, category, available, item_id))
            conn.commit()
            flash('Menu item updated successfully', 'success')

        elif 'delete_item' in request.form:
            item_id = request.form['item_id']
            cursor.execute('DELETE FROM menu_items WHERE id=%s', (item_id,))
            conn.commit()
            flash('Menu item deleted successfully', 'success')

    cursor.execute('SELECT * FROM menu_items ORDER BY category, name')
    menu_items = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('menu.html', menu_items=menu_items)

@app.route('/orders', methods=['GET', 'POST'])
@login_required
def orders():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        if 'create_order' in request.form:
            customer_name = request.form['customer_name']
            table_id = request.form['table_id']

            # Create customer if not exists
            cursor.execute('SELECT id FROM customers WHERE name = %s', (customer_name,))
            customer = cursor.fetchone()
            if not customer:
                cursor.execute('INSERT INTO customers (name) VALUES (%s)', (customer_name,))
                customer_id = cursor.lastrowid
            else:
                customer_id = customer['id']

            # Create order
            cursor.execute('INSERT INTO orders (customer_id, table_id) VALUES (%s, %s)', (customer_id, table_id))
            order_id = cursor.lastrowid

            # Update table status
            cursor.execute('UPDATE `tables` SET status = %s WHERE id = %s', ('occupied', table_id))

            conn.commit()
            flash(f'Order #{order_id} created successfully', 'success')
            return redirect(url_for('order_detail', order_id=order_id))

    # Get available tables
    cursor.execute('SELECT * FROM `tables` WHERE status = %s', ('available',))
    available_tables = cursor.fetchall()

    # Get recent orders
    cursor.execute('''
        SELECT o.*, c.name as customer_name, t.table_number
        FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.id
        LEFT JOIN `tables` t ON o.table_id = t.id
        ORDER BY o.order_time DESC LIMIT 20
    ''')
    recent_orders = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('orders.html', available_tables=available_tables, recent_orders=recent_orders)

@app.route('/order/<int:order_id>', methods=['GET', 'POST'])
def order_detail(order_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        if 'add_item' in request.form:
            menu_item_id = request.form['menu_item_id']
            quantity = int(request.form['quantity'])

            # Get menu item price
            cursor.execute('SELECT price FROM menu_items WHERE id = %s', (menu_item_id,))
            price = cursor.fetchone()['price']

            # Add to order_items
            cursor.execute('INSERT INTO order_items (order_id, menu_item_id, quantity, price) VALUES (%s, %s, %s, %s)',
                         (order_id, menu_item_id, quantity, price))

            # Update order total
            cursor.execute('UPDATE orders SET total_amount = total_amount + (%s * %s) WHERE id = %s',
                         (quantity, price, order_id))

            conn.commit()
            flash('Item added to order', 'success')

        elif 'update_status' in request.form:
            status = request.form['status']
            cursor.execute('UPDATE orders SET status = %s WHERE id = %s', (status, order_id))

            if status == 'served':
                # Free the table
                cursor.execute('UPDATE `tables` SET status = %s WHERE id = (SELECT table_id FROM orders WHERE id = %s)', ('available', order_id))

            conn.commit()
            flash('Order status updated', 'success')

    # Get order details
    cursor.execute('''
        SELECT o.*, c.name as customer_name, t.table_number
        FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.id
        LEFT JOIN `tables` t ON o.table_id = t.id
        WHERE o.id = %s
    ''', (order_id,))
    order = cursor.fetchone()

    # Get order items
    cursor.execute('''
        SELECT oi.*, mi.name, mi.description
        FROM order_items oi
        JOIN menu_items mi ON oi.menu_item_id = mi.id
        WHERE oi.order_id = %s
    ''', (order_id,))
    order_items = cursor.fetchall()

    # Get menu items for adding
    cursor.execute('SELECT * FROM menu_items WHERE available = TRUE ORDER BY category, name')
    menu_items = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('order_detail.html', order=order, order_items=order_items, menu_items=menu_items)

@app.route('/billing/<int:order_id>')
@login_required
def billing(order_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get order details
    cursor.execute('''
        SELECT o.*, c.name as customer_name, c.phone, c.email, t.table_number
        FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.id
        LEFT JOIN `tables` t ON o.table_id = t.id
        WHERE o.id = %s
    ''', (order_id,))
    order = cursor.fetchone()

    # Get order items
    cursor.execute('''
        SELECT oi.*, mi.name
        FROM order_items oi
        JOIN menu_items mi ON oi.menu_item_id = mi.id
        WHERE oi.order_id = %s
    ''', (order_id,))
    order_items = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('billing.html', order=order, order_items=order_items)

@app.route('/process_payment/<int:order_id>', methods=['POST'])
@login_required
def process_payment(order_id):
    payment_method = request.form['payment_method']
    amount = float(request.form['amount'])

    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert payment
    cursor.execute('INSERT INTO payments (order_id, amount, payment_method, status) VALUES (%s, %s, %s, %s)',
                 (order_id, amount, payment_method, 'completed'))

    # Update order status
    cursor.execute('UPDATE orders SET status = %s WHERE id = %s', ('served', order_id))

    # Free the table
    cursor.execute('UPDATE `tables` SET status = %s WHERE id = (SELECT table_id FROM orders WHERE id = %s)', ('available', order_id))

    conn.commit()
    cursor.close()
    conn.close()

    flash('Payment processed successfully', 'success')
    return redirect(url_for('billing', order_id=order_id))

@app.route('/reports')
@login_required
def reports():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Daily sales report
    cursor.execute('''
        SELECT DATE(order_time) as date, COUNT(*) as orders_count, SUM(total_amount) as total_revenue
        FROM orders
        WHERE status != 'cancelled'
        GROUP BY DATE(order_time)
        ORDER BY date DESC LIMIT 30
    ''')
    daily_sales = cursor.fetchall()

    # Popular items
    cursor.execute('''
        SELECT mi.name, SUM(oi.quantity) as total_quantity, SUM(oi.quantity * oi.price) as total_revenue
        FROM order_items oi
        JOIN menu_items mi ON oi.menu_item_id = mi.id
        JOIN orders o ON oi.order_id = o.id
        WHERE o.status != 'cancelled'
        GROUP BY mi.id, mi.name
        ORDER BY total_quantity DESC LIMIT 10
    ''')
    popular_items = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('reports.html', daily_sales=daily_sales, popular_items=popular_items)

@app.route('/about')
@login_required
def about():
    return render_template('about.html')

@app.route('/api/menu_items')
@login_required
def api_menu_items():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM menu_items WHERE available = TRUE ORDER BY category, name')
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(items)

@app.route('/place_order', methods=['POST'])
def place_order():
    try:
        customer_name = request.form.get('customer_name')
        table_id = request.form.get('table_id')
        order_items = request.form.get('order_items')

        if not customer_name or not table_id or not order_items:
            return jsonify({'success': False, 'message': 'Missing required fields'})

        order_items = json.loads(order_items)
        if not order_items:
            return jsonify({'success': False, 'message': 'No items in order'})

        conn = get_db_connection()
        cursor = conn.cursor()

        # Create customer if not exists
        cursor.execute('SELECT id FROM customers WHERE name = %s', (customer_name,))
        customer = cursor.fetchone()
        if not customer:
            cursor.execute('INSERT INTO customers (name) VALUES (%s)', (customer_name,))
            customer_id = cursor.lastrowid
        else:
            customer_id = customer[0]

        # Create order
        cursor.execute('INSERT INTO orders (customer_id, table_id) VALUES (%s, %s)', (customer_id, table_id))
        order_id = cursor.lastrowid

        # Add order items
        total_amount = 0
        for item in order_items:
            item_total = item['price'] * item['quantity']
            total_amount += item_total
            cursor.execute('INSERT INTO order_items (order_id, menu_item_id, quantity, price) VALUES (%s, %s, %s, %s)',
                         (order_id, item['id'], item['quantity'], item['price']))

        # Update order total
        cursor.execute('UPDATE orders SET total_amount = %s WHERE id = %s', (total_amount, order_id))

        # Update table status
        cursor.execute('UPDATE `tables` SET status = %s WHERE id = %s', ('occupied', table_id))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True, 'order_id': order_id})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == "__main__":
    init_admin_user()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
