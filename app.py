"""
CRATE - Simple E-commerce Store (Flask)
-----------------------------------------
Same core features as before, redesigned front end:
- Product listing + product detail page
- Shopping cart (session-based)
- User registration/login (Flask-Login)
- Order processing (saved to database)

Run with: python app.py
Then open: http://127.0.0.1:5000
"""

from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user,
    login_required, logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# ---------------------------------------------------------
# App setup
# ---------------------------------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to continue.'


# ---------------------------------------------------------
# Database Models
# ---------------------------------------------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(300))
    stock = db.Column(db.Integer, default=10)

    @property
    def sku(self):
        """A spec-sheet style product code, e.g. SKU-0004."""
        return f"SKU-{self.id:04d}"

    @property
    def stock_bars(self):
        """Turns raw stock count into a 0-4 'signal bar' level for the UI."""
        if self.stock <= 0:
            return 0
        elif self.stock <= 5:
            return 1
        elif self.stock <= 10:
            return 2
        elif self.stock <= 15:
            return 3
        return 4


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Placed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True)


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product_name = db.Column(db.String(120))
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------------------------------------------------------
# Helper: read the cart out of the session
# ---------------------------------------------------------
def get_cart_details():
    cart = session.get('cart', {})
    items = []
    total = 0
    for product_id, qty in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            subtotal = round(product.price * qty, 2)
            total += subtotal
            items.append({'product': product, 'qty': qty, 'subtotal': subtotal})
    return items, round(total, 2)


# ---------------------------------------------------------
# Routes: Product listing + details
# ---------------------------------------------------------
@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)


# ---------------------------------------------------------
# Routes: Cart
# ---------------------------------------------------------
@app.route('/cart')
def cart():
    items, total = get_cart_details()
    return render_template('cart.html', items=items, total=total)


@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    qty = int(request.form.get('quantity', 1))

    cart = session.get('cart', {})
    key = str(product_id)
    cart[key] = cart.get(key, 0) + qty
    session['cart'] = cart
    session.modified = True

    flash(f'Added {qty} x {product.name} to your cart.', 'success')
    return redirect(url_for('index'))


@app.route('/update_cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    qty = int(request.form.get('quantity', 1))
    cart = session.get('cart', {})
    key = str(product_id)
    if qty <= 0:
        cart.pop(key, None)
    else:
        cart[key] = qty
    session['cart'] = cart
    session.modified = True
    return redirect(url_for('cart'))


@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    cart.pop(str(product_id), None)
    session['cart'] = cart
    session.modified = True
    flash('Item removed from cart.', 'info')
    return redirect(url_for('cart'))


# ---------------------------------------------------------
# Routes: Checkout / Order processing
# ---------------------------------------------------------
@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    items, total = get_cart_details()

    if not items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('index'))

    if request.method == 'POST':
        order = Order(user_id=current_user.id, total=total)
        db.session.add(order)
        db.session.flush()

        for entry in items:
            product = entry['product']
            item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                price=product.price,
                quantity=entry['qty']
            )
            db.session.add(item)
            product.stock = max(0, product.stock - entry['qty'])

        db.session.commit()

        session['cart'] = {}
        session.modified = True

        return redirect(url_for('order_success', order_id=order.id))

    return render_template('checkout.html', items=items, total=total)


@app.route('/order_success/<int:order_id>')
@login_required
def order_success(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        return redirect(url_for('index'))
    return render_template('order_success.html', order=order)


@app.route('/my_orders')
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('my_orders.html', orders=orders)


# ---------------------------------------------------------
# Routes: Auth
# ---------------------------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('That username is already taken.', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('That email is already registered.', 'danger')
            return redirect(url_for('register'))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))

        flash('Invalid username or password.', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# ---------------------------------------------------------
# Seed sample products
# ---------------------------------------------------------
def seed_data():
    if Product.query.count() > 0:
        return

    sample_products = [
        Product(
            name='Wireless Headphones',
            description='Over-ear noise-cancelling headphones with 30hr battery life.',
            price=2499.00,
            image_url='/static/images/wireless-headphones.jpg',
            stock=20
        ),
        Product(
            name='Mechanical Keyboard',
            description='60% RGB backlit mechanical keyboard with hot-swappable switches.',
            price=3199.00,
            image_url='/static/images/mechanical-keyboard.jpg',
            stock=15
        ),
        Product(
            name='Smart Watch',
            description='Rugged sports smartwatch with heart-rate monitor and call support.',
            price=4999.00,
            image_url='/static/images/smart-watch.jpg',
            stock=10
        ),
        Product(
            name='Bluetooth Speaker',
            description='Portable speaker with RGB lighting and rich bass.',
            price=1799.00,
            image_url='/static/images/bluetooth-speaker.png',
            stock=25
        ),
        Product(
            name='Laptop Backpack',
            description='Water-resistant laptop sleeve bag with padded handles.',
            price=1299.00,
            image_url='/static/images/laptop-backpack.jpg',
            stock=30
        ),
        Product(
            name='USB-C Hub',
            description='7-in-1 USB-C hub with HDMI, Ethernet, SD/microSD, and USB 3.0.',
            price=999.00,
            image_url='/static/images/usb-c-hub.jpg',
            stock=18
        ),
    ]
    db.session.add_all(sample_products)
    db.session.commit()
    print('Sample products added.')


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True)
