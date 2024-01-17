from itertools import product
import os
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(os.path.abspath(os.path.dirname(__file__)),'db.sqlite3')
app.config['SECRET_KEY']="ihatemad1"
db = SQLAlchemy(app)
app.app_context().push()

#database

class Products(db.Model):
    __tablename__ ="products"
    product_id = db.Column(db.String(100), primary_key=True, unique=True)
    product_name = db.Column(db.String(100))
    product_descp = db.Column(db.String(100))
    product_qty = db.Column(db.Integer)
    product_pr = db.Column(db.Integer)
    categories = db.relationship('Categories', secondary='Products_Categories', back_populates='products')

class Categories(db.Model):
    __tablename__ ="categories"
    category_id = db.Column(db.String(100), primary_key=True)
    category_name = db.Column(db.String(100))
    products = db.relationship('Products', secondary='Products_Categories', back_populates='categories')

class PC(db.Model):
    __tablename__ = "Products_Categories"
    pc_id = db.Column(db.String(100), primary_key=True, unique=True)
    product_id = db.Column(db.String(100), db.ForeignKey("products.product_id"), nullable=False)
    category_id = db.Column(db.String(100), db.ForeignKey("categories.category_id"), nullable=False)
    def __init__(self, pc_id, product_id, category_id):
        self.pc_id = pc_id
        self.product_id = product_id
        self.category_id = category_id

class User(db.Model):
    __tablename__ = 'App_Users'
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100))
    user_username = db.Column(db.String(100), unique=True)
    user_password = db.Column(db.String(100))
    user_contact = db.Column(db.String(100))
    user_email = db.Column(db.String(100))
    user_address = db.Column(db.String(100))
    user_city = db.Column(db.String(100))
    orders = db.relationship('Order', backref='user', lazy=True)

class Order(db.Model):
    __tablename__ = "App_Orders"
    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('App_Users.user_id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    order_items = db.Column(db.JSON, nullable=False)
    order_amount = db.Column(db.Integer, nullable=False) 
    def __init__(self, user_id, order_items, order_amount):
        self.user_id = user_id
        self.order_items = order_items
        self.order_amount = order_amount

class Cart(db.Model):
    __tablename__ = 'Cart'
    cart_id = db.Column(db.String(100), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('App_Users.user_id'), nullable=False)
    product_id = db.Column(db.String(100), db.ForeignKey('products.product_id'), nullable=False)
    product_pr = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    cproduct_qty = db.Column(db.Integer, nullable=False)

db.create_all()

#login/signin

@app.route('/user-sign-up', methods=['GET', 'POST'], endpoint='user_sign_up')
def usgnup():   
    if request.method == "GET":
        return render_template("user_sign_up.html")
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username'] 
        contact = request.form['contact']
        email = request.form['email']
        address = request.form['address']
        city = request.form['city']
        password = request.form['password']
        c_password = request.form['confirm_password']
        user_exists = db.session.query(User).filter_by(user_username=username).first() is not None
        if user_exists:
            return render_template('account_exists.html')
        else:
            if password == c_password:
                user = User(user_name=name, user_username=username, user_email=email, user_password=password, user_contact=contact, user_address=address, user_city=city)
                db.session.add(user)
                db.session.commit()
                session['uid'] = user.user_id
                products = Products.query.all()
                return redirect(url_for('home'))
            else:
                return render_template("password_error1.html")

@app.route('/user-sign-in', methods=['GET','POST'],endpoint='user_sign_in')
def usgnin(): 
    if request.method == "GET":
        return render_template("user_sign_in.html") 
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.session.query(User).filter_by(user_username=username).first()  
        if user and user.user_password == password:
            session['uid'] = user.user_id
            return redirect(url_for('home'))
        else:
            return render_template("incorrect1.html")

@app.route('/admin-sign-in', methods=['GET', 'POST'], endpoint='admin_sign_in')
def admin_sign_in():
    if request.method == "GET":
        return render_template("admin_sign_in.html") 
    elif request.method == 'POST':
        employee_id = request.form['employeeID']

        if employee_id == 'A1001':
            session['is_admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template("incorrect2.html")

#main pages

@app.route('/home')
def home():
    user = User.query.filter_by(user_id=session['uid']).first()
    return render_template('home.html',user=user)

@app.route('/categories')
def categories():
    categories = Categories.query.all()  
    return render_template('categories.html', categories=categories)

@app.route('/categories_admin')
def categories_admin():
    categories = Categories.query.all()  
    return render_template('categories_admin.html', categories=categories)

@app.route('/products-by-category/<string:category>', methods=['GET', 'POST'])
def products_by_category(category):
    selected_category = Categories.query.filter_by(category_name=category).first()
    if selected_category:
        category_products = selected_category.products
        if request.method == 'POST':
            product_id = request.form['product_id']
            quantity = int(request.form['cproduct_qty'])
            cart_entry = Cart(
                user_id=session['uid'],
                product_id=product_id,
                product_name=product.product_name,
                product_pr=product.product_pr,
                cproduct_qty=quantity
            )
            db.session.add(cart_entry)
            db.session.commit()
        return render_template('products_by_category.html', selected_category=selected_category)

@app.route('/products-by-category-admin/<string:category>', methods=['GET', 'POST'])
def products_by_category_admin(category):
    selected_category = Categories.query.filter_by(category_name=category).first()
    if selected_category:
        category_products = selected_category.products
    return render_template('products_by_category_admin.html', selected_category=selected_category)

#functionalities

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if request.method == 'POST':
        product_id = request.form['product_id']
        quantity = int(request.form['quantity'])
        user_id = session.get('uid')
        if user_id and quantity > 0:
            product = db.session.query(Products).get(product_id)
            if product and quantity <= product.product_qty:
                cart_count = Cart.query.count()
                cart_id = f'CRT{cart_count + 1}'
                cart_entry = Cart(
                    cart_id=cart_id,
                    user_id=user_id,
                    product_id=product_id,
                    product_name=product.product_name,
                    product_pr=product.product_pr,
                    cproduct_qty=quantity
                )
                db.session.add(cart_entry)
                db.session.commit()
                return "Product added to cart!"
            else:
                return "Invalid product or quantity"
        else:
            return "User not logged in or invalid quantity"
    else:
        return "Invalid request method"

@app.route('/cart')
def cart():
    if 'uid' in session:
        user_id = session['uid']
        user = User.query.get(user_id)
        if not user:
            return render_template('user_nf.html')
        cart_items = Cart.query.filter_by(user_id=user_id).all()
        total_amount = 0
        for cart_item in cart_items:
            total_amount += cart_item.cproduct_qty * cart_item.product_pr
        return render_template('cart.html', user=user, cart_items=cart_items, total_amount=total_amount)
    else:
        return redirect(url_for('home'))

@app.route('/place_order', methods=['POST'])
def place_order():
    if session.get('uid'):
        user_id = session['uid']
        user = User.query.get(user_id)
        cart_items = Cart.query.filter_by(user_id=user_id).all()
        order_items = {}
        total_amount = 0
        for cart_item in cart_items:
            product_name = cart_item.product_name
            quantity = cart_item.cproduct_qty
            price_per_piece = cart_item.product_pr
            total_price = quantity * price_per_piece
            order_items[product_name] = [quantity*2, price_per_piece, total_price]
            total_amount += total_price
            product = Products.query.get(cart_item.product_id)
            if product:
                product.product_qty -= (quantity*2)  
                db.session.commit()
        new_order = Order(user_id=user_id, order_items=order_items, order_amount=total_amount)
        db.session.add(new_order)
        db.session.commit()
        Cart.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        return render_template('order_placed.html', order=new_order, total_amount=total_amount)
    else:
        return redirect(url_for('home'))

@app.route('/order-history/<int:user_id>')
def order_history(user_id):
    user = User.query.get(user_id)
    if user:
        orders = Order.query.filter_by(user_id=user_id).all()
        return render_template('order_history.html', user=user, orders=orders)
    else:
        return render_template('user_nf.html')

#admin

@app.route('/admin')
def admin_dashboard():
    categories = Categories.query.all()  
    return render_template('admin_dashboard.html',categories=categories)

@app.route('/admin/see-users')
def see_users():
    all_users = User.query.all()
    return render_template('see_users.html', all_users=all_users)

@app.route('/admin/see-orders')
def see_orders():
    all_orders = Order.query.all()
    return render_template('see_orders.html', all_orders=all_orders, user=None) 

@app.route('/admin/add-category',methods=['GET','POST'])
def add_category():
    if request.method == 'POST':
        category_id = request.form['category_id']
        category_name = request.form['category_name']
        new_category = Categories(category_id=category_id,category_name=category_name)
        db.session.add(new_category)
        db.session.commit()
        flash("Category added successfully!", "success")
        return redirect(url_for('categories_admin'))
    return render_template('add_category.html')

@app.route('/admin/add-product', methods=['GET', 'POST'])
def add_product():
    categories = Categories.query.all()
    if request.method == 'POST':
        category_name = request.form['category_name']
        product_name = request.form['product_name']
        product_descp = request.form['product_descp']
        product_qty = int(request.form['product_qty']) 
        product_pr = int(request.form['product_pr'])   
        category = Categories.query.filter_by(category_name=category_name).first()
        if category:
            highest_product_id = db.session.query(func.max(Products.product_id)).scalar()
            if highest_product_id:
                highest_number = int(highest_product_id[1:])
                next_product_number = highest_number + 1
            else:
                next_product_number = 1
            new_product_id = f"P{next_product_number:02}"
            new_product = Products(
                product_id=new_product_id,
                product_name=product_name,
                product_descp=product_descp,
                product_qty=product_qty,
                product_pr=product_pr
            )
            db.session.add(new_product)
            pc_id = f"CP{next_product_number:02}"
            pc_entry = PC(pc_id=pc_id, product_id=new_product_id, category_id=category.category_id)
            db.session.add(pc_entry)
            db.session.commit()
            flash("Product added successfully!", "success")
            return redirect(url_for('categories_admin'))
        else:
            flash("Category not found!", "error")
    return render_template('add_product.html', categories=categories)

@app.route('/admin/edit_category', methods=['GET', 'POST'])
def edit_category():
    categories = Categories.query.all() 
    if request.method == 'POST':
        original_category_name = request.form['original_category_name']
        new_category_name = request.form['new_category_name']
        category = Categories.query.filter_by(category_name=original_category_name).first()
        if category:
            category.category_name = new_category_name
            db.session.commit()
            flash("Category updated successfully!", "success")
            return redirect(url_for('categories_admin'))
        else:
            flash("Original category not found!", "error")
    return render_template('edit_category.html', categories=categories)

@app.route('/admin/edit-product', methods=['GET', 'POST'])
def edit_product():
    categories = Categories.query.all()
    selected_category = None
    selected_product = None
    products = []
    if request.method == 'POST':
        category_id = request.form['category']
        product_id = request.form['product']
        category = Categories.query.get(category_id)
        if category:
            selected_category = category
            products = Products.query.join(PC, Products.product_id == PC.product_id) \
                                    .filter(PC.category_id == category_id).all()
            if product_id:
                selected_product = Products.query.get(product_id)
                if selected_product:
                    selected_product.product_name = request.form['product_name']
                    selected_product.product_descp = request.form['product_description']
                    selected_product.product_qty = int(request.form['product_quantity'])
                    selected_product.product_pr = int(request.form['product_price'])
                    db.session.commit()
                    flash("Product updated successfully!", "success")
                else:
                    flash("Product not found!", "error")
        else:
            flash("Category not found!", "error")
        return redirect(url_for('categories_admin'))
    elif request.method == 'GET':
        category_id = request.args.get('category')
        if category_id:
            selected_category = Categories.query.get(category_id)
            products = Products.query.join(PC, Products.product_id == PC.product_id) \
                                    .filter(PC.category_id == category_id).all()
    return render_template(
        'edit_product.html',
        categories=categories,
        selected_category=selected_category,
        selected_product=selected_product,
        products=products
    )

@app.route('/admin/delete-category', methods=['GET', 'POST'])
def delete_category():
    categories = Categories.query.all() 
    if request.method == 'POST':
        category_name = request.form['category_name']
        category = Categories.query.filter_by(category_name=category_name).first()
        if category:
            products_to_delete = Products.query.filter(Products.categories.contains(category)).all()
            for product in products_to_delete:
                db.session.delete(product)
            db.session.delete(category)
            db.session.commit()
            flash("Category and its products deleted successfully!", "success")
            return redirect(url_for('categories_admin'))
        else:
            flash("Category not found!", "error")
    return render_template('delete_category.html', categories=categories)

@app.route('/admin/delete-product', methods=['GET', 'POST'])
def delete_product():
    categories = Categories.query.all()
    selected_category = None
    if request.method == 'POST':
        category_id = request.form['category']
        product_id = request.form['product']
        category = Categories.query.get(category_id)
        product = Products.query.get(product_id)
        if category and product:
            if product in category.products:
                category.products.remove(product)
                db.session.delete(product)
                db.session.commit()
                flash("Product deleted successfully!", "success")
                return redirect(url_for('categories_admin'))
            else:
                flash("Product not found in the selected category!", "error")
        else:
            flash("Category or product not found!", "error")
    else:
        category_id = request.form.get('category')
        if category_id:
            selected_category = Categories.query.get(category_id)
    return render_template('delete_product.html', categories=categories, selected_category=selected_category)

#others

@app.route('/profile')
def profile():
    if 'uid' in session:
        user_id = session['uid']
        user = User.query.get(user_id)
        if user:
            return render_template('profile.html', user=user)
        else:
            return render_template('user_nf.html')
    else:
        return redirect(url_for('home'))

@app.route('/edit-profile/<string:user_id>')
def edit_profile(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    if user:
        return render_template('edit_profile.html', user=user)
    else:
        return render_template('user_nf.html')

@app.route('/update-profile/<string:user_id>', methods=['POST'])
def update_profile(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    if user:
        user.user_username = request.form['username']
        user.user_email = request.form['email']
        user.user_name = request.form['name']
        user.user_contact = request.form['contact']
        user.user_address = request.form['address']
        user.user_city = request.form['city']
        db.session.commit()
        return redirect(url_for('profile', user_id=user.user_id))
    else:
        return render_template('user_nf.html')

@app.route('/logout')
def logout():
    session.pop('uid', None)
    return redirect(url_for('main_page'))

@app.route('/') 
def main_page():
    return render_template('main_page.html')

if __name__=='__main__':
    app.run(debug=True)