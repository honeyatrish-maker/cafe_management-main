# Continental Cafe Management System

A complete full-stack cafe management system built with Python Flask, MySQL, HTML5, CSS3, and JavaScript.

## Features

### Public Features
- Responsive menu display with search and filtering
- Shopping cart functionality with local storage persistence
- Order placement with customer details
- Dark/Light theme toggle
- Mobile-friendly design

### Admin Features
- Secure admin login system with session management
- Dashboard with key statistics and recent orders
- Menu management (add, edit, delete menu items with categories)
- Order management (view orders, update status, detailed order view)
- Billing and payment processing with printable receipts
- Customer and table management
- Daily sales reports and analytics
- Form validation and error handling

## Tech Stack

- **Backend:** Python Flask
- **Database:** MySQL
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla JS)
- **Architecture:** MVC pattern with separate concerns
- **Styling:** Custom CSS with CSS Variables for theming

## Project Structure

```
continental-cafe/
│
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── database.sql             # Database schema and sample data
├── README.md                # This file
├── static/
│   ├── css/
│   │   └── style.css        # Main stylesheet with theme support
│   ├── js/
│   │   └── script.js        # JavaScript functionality
│   └── images/              # Static images
├── templates/
│   ├── public_base.html     # Public-facing base template
│   ├── index.html           # Public menu page
│   ├── base.html            # Admin base template
│   ├── login.html           # Admin login page
│   ├── dashboard.html       # Admin dashboard
│   ├── menu.html            # Menu management
│   ├── orders.html          # Orders list
│   ├── order_detail.html    # Order details
│   ├── billing.html         # Billing page
│   ├── reports.html         # Reports page
│   └── about.html           # About page
├── .github/
│   └── copilot-instructions.md # AI assistant instructions
└── .venv/                   # Virtual environment
```

## Installation and Setup

### Prerequisites

- Python 3.7+
- MySQL Server
- Git (optional)

### Step 1: Clone or Download the Project

Download the project files to your local machine.

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Setup MySQL Database

1. Start your MySQL server
2. Create a new database (optional, the app will create it)
3. Run the database.sql file to create tables and insert sample data:

```sql
mysql -u root -p < database.sql
```

Or copy and paste the contents into your MySQL client.

### Step 4: Configure Database Connection

Edit `app.py` and update the `DB_CONFIG` dictionary with your MySQL credentials:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'cafe_db'
}
```

### Step 5: Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## Usage

### Public Access
- Visit `http://localhost:5000` to view the menu
- Browse items, add to cart, and place orders
- Toggle between light and dark themes

### Admin Access
- Visit `http://localhost:5000/login` to access admin panel
- Default credentials: `admin` / `admin123`
- Manage menu items, view orders, generate reports

## API Endpoints

- `GET /` - Public menu
- `POST /place_order` - Submit order
- `GET /login` - Admin login
- `GET /dashboard` - Admin dashboard
- `GET /menu` - Menu management
- `GET /orders` - Orders list
- `GET /reports` - Sales reports

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.
    'user': 'your_mysql_username',
    'password': 'your_mysql_password',
    'database': 'cafe_management'
}
```

### Step 5: Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### Step 6: Access the Application

1. Open your browser and go to `http://localhost:5000`
2. Login with the default admin credentials:
   - Username: `admin`
   - Password: `admin123`

## Usage

### Admin Login
- Use the provided credentials to log in
- Session management keeps you logged in across pages

### Dashboard
- View key statistics like today's orders, revenue, menu items, and pending orders
- Quick access to main functions

### Menu Management
- Add new menu items with name, description, price, and category
- Edit existing items
- Delete items (with confirmation)
- Mark items as available/unavailable

### Order Management
- Create new orders for customers
- Assign tables to orders
- Add menu items to orders
- Update order status (pending → preparing → ready → served)
- View order history

### Billing
- Generate bills for completed orders
- Process payments (cash, card, online)
- Print bills
- Mark orders as paid

### Reports
- View daily sales reports
- See popular menu items
- Track revenue over time

## Database Schema

The system uses the following tables:

- `users` - Admin user accounts
- `menu_items` - Cafe menu items
- `tables` - Table information
- `customers` - Customer details
- `orders` - Order information
- `order_items` - Items in each order
- `payments` - Payment records

## Security Features

- Password hashing using Werkzeug
- Session-based authentication
- CSRF protection (Flask-WTF not implemented but can be added)
- Input validation on forms

## Responsive Design

The application is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones

## Future Enhancements

- QR code bill generation
- Dark/light mode toggle
- Analytics charts with Chart.js
- PDF invoice download
- Inventory management
- Customer loyalty program
- Email notifications

## Troubleshooting

### Database Connection Issues
- Ensure MySQL server is running
- Check database credentials in `app.py`
- Verify database name exists

### Import Errors
- Install all requirements: `pip install -r requirements.txt`
- Ensure Python 3.7+ is being used

### Port Already in Use
- Change the port in `app.py`: `app.run(debug=True, host='0.0.0.0', port=5001)`

### Permission Issues
- Ensure proper permissions for database user
- Check file permissions for the project directory

## Contributing

Feel free to fork this project and add your own features!

## License

This project is open source and available under the MIT License.
