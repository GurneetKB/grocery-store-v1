# 🛒 The OneStop Store – Grocery Store (V1)

A full-stack **Grocery Store Web Application** with role-based access for users and admins. Designed to simulate a complete e-commerce workflow including product browsing, cart management, and order processing.


---


## 🚀 Key Features

### 👤 User

* Register / Login
* Browse products by category
* Add items to cart (with quantity control)
* Place orders
* View order history
* Edit profile

### 🛠 Admin

* Add / Edit / Delete categories
* Add / Edit / Delete products
* View users
* Monitor orders


---


## 🗂 Core Database Models

* **Products** (name, description, price, stock)
* **Categories**
* **Product–Category Relation (PC)**
* **User**
* **Cart**
* **Order**

Implements structured relational mapping and dynamic cart-to-order workflow.


---


## 🔄 Application Flow

1. Home → Admin Sign-in / User Login / Sign-up
2. User Dashboard → Profile, Categories, Cart, Orders
3. Category → View products → Add to cart
4. Cart → Place order → Updates database
5. Admin Dashboard → Full product & category management


---


## 🧠 Tech Stack

* **Flask**
* **SQLAlchemy**
* **SQLite**
* HTML/CSS (Pastel minimal UI)


---


## ▶️ Run Locally

```bash
git clone https://github.com/GurneetKB/grocery-store-v1.git
cd grocery-store-v1

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt
python app.py
```


---


## 👩‍💻 Author

**Gurneet Kaur Bhuller**
IIT Madras – BS in Data Science


---
