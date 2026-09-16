# Simple E-Commerce Store

A basic full-stack e-commerce web application developed as part of my Full Stack Development Internship at CodeAlpha.

The application allows users to browse products, view product details, add products to a shopping cart, place orders, and manage their accounts.

## 🚀 Features

- 🛍️ Product listing
- 📦 Product details page
- 🛒 Shopping cart
- 💳 Order processing
- 👤 User registration and login
- 🔐 User authentication
- 🗄️ Database for products, users, and orders
- 📱 Responsive user interface

## 🛠️ Technologies Used

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Django (Python)

### Database
- SQLite

## 📂 Project Structure

```text
ecommerce-store/
│
├── manage.py
├── requirements.txt
├── README.md
│
├── ecommerce/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── products/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── users/
│   ├── models.py
│   ├── views.py
│   └── urls.py
│
├── orders/
│   ├── models.py
│   ├── views.py
│   └── urls.py
│
├── templates/
│   ├── home.html
│   ├── products.html
│   ├── product_detail.html
│   ├── cart.html
│   ├── login.html
│   └── register.html
│
└── static/
    ├── css/
    ├── js/
    └── images/
