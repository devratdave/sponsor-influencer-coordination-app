from app import app, db
from flask import render_template, redirect, url_for, flash, request
from forms import UserForm, LoginForm, SearchForm, ProductForm, CategoryForm, ProductUpdateForm
from models import User, Product, Category, Cart
from flask_login import login_user, login_required, logout_user, current_user

@app.context_processor
def base():
    form= SearchForm()
    return dict(form=form)


## Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form= UserForm()
    if form.validate_on_submit():

        ## Validates if other users exist with the same username, email
        email_verification= User.query.filter_by(email= form.email.data).first()
        username_verification= User.query.filter_by(username= form.username.data).first()
        if email_verification:
            flash('This email is already in use')
            return redirect(url_for('signup'))
        elif username_verification:
                flash('This username is taken')
                return redirect(url_for('signup'))
        
        ## Creates a user object and adds it into the database
        else:
            user= User(fullname= form.name.data, 
                    email= form.email.data,
                    username= form.username.data,
                    password= form.password.data)
            db.session.add(user)
            db.session.commit()
            user= User.query.filter_by(username=form.username.data).first()

            ## First user of the app is the admin
            if user.id==1:
                user.role='admin'
                db.session.commit()
                flash('Admin account for this app has been created')
                login_user(user)
                return redirect('/admin')
            flash('Account created succesfully')
            login_user(user)
            return redirect(url_for('home'))

    return render_template('signup.html', form=form)


## Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form= LoginForm()
    if form.validate_on_submit():
        user= User.query.filter_by(username= form.username.data).first()
        if user:
            if user.password==form.password.data:
                if user.role=='admin':
                    login_user(user)
                    flash('Welcome back admin')
                    return redirect('/admin')
                else:
                    login_user(user)
                    flash('You\'ve succesfully logged in. Welcome!')
                    return redirect('home')
            else:
                flash('You\'ve entered the wrong credentials, try again')
                return redirect('login')
        else:
            flash('The user doesn\'t exist')
            return redirect(url_for('signup'))

    return render_template('login.html', form=form)


## Home Route
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    products= Product.query.filter().all()
    categories= Category.query.filter().all()
    cart_of_user= Cart.query.filter_by(user_id=current_user.id).all()
    if request.method=='POST':
        ## Adding the product in the cart
        product_id= request.form.get('submit_button')
        product= Product.query.filter_by(id=product_id).first()
        if product:
            quantity= int(request.form.get('quantity'))
            ## Check if the product is already added in the cart, then updates the quantity
            cart_exists= Cart.query.filter_by(product=product.name, user_id=current_user.id).first()
            if product.stock < quantity:
                flash("Sorry we dont have this much stock for this product, reduce the quantity and try again")
            elif cart_exists:
                if cart_exists.quantity >= product.stock:
                    flash("No more quantity of this product can be added")
                else:
                    cart_exists.quantity=cart_exists.quantity+quantity  
                    flash('Product has been updated in cart')
            else:
                cart_product= Cart(product=product.name, user_id=current_user.id , quantity=quantity, unitprice=product.price, unit=product.unit)
                db.session.add(cart_product)
                flash('Product has been added to cart')

            db.session.commit()
            return redirect(url_for('home'))
        
    return render_template('home.html', products=products, categories=categories, cart_products=cart_of_user)


## Dashboard endpoints tells you the user details
@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    products= Product.query.all()
    categories= Category.query.all()
    category_units_sold=[]
    category_name_labels=[]
    for category in categories:
        category_name_labels.append(category.name)
        category_units_values=0
        for product in products:
            if product.category==category.name:
                category_units_values+=product.units_sold
        category_units_sold.append(category_units_values)
    name_labels= []
    units_sold= []
    for product in products:
        name_labels.append(product.name)
        units_sold.append(product.units_sold)
    return render_template('dashboard.html', product_labels= name_labels, product_values= units_sold,
                           category_labels=category_name_labels,
                           category_values= category_units_sold)


## Logs out the user/admin
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
	logout_user()
	flash("You Have Been Logged Out!  Thanks For Stopping By...")
	return redirect(url_for('login'))


## Searchbar for searching products based on their name or category-name.
@app.route('/search', methods=['POST'])
@login_required
def search():
    form= SearchForm()
    products= Product.query
    if form.validate_on_submit:
        searched= form.searched.data
        results= products.filter(Product.name.like(f'%{searched}%') | Product.category.like(f'%{searched}%')).all()
        return render_template('searched_results.html', form=form, searched=searched,
                               results=results)


## Admin route, accessible for anyone with the role 'admin'
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if current_user.role=='admin':
        products= Product.query.filter().all()
        categories= Category.query.filter().all()
        
        ## All the products in the inventory can be viewed and deleted from here
        ## Routes for adding new products and categories is also present on this page
        if request.method=='POST':
            product_id= request.form.get('product_deletion')
            product_id_forupdation= request.form.get('product_updation')
            category_id= request.form.get('category_deletion')
            if product_id_forupdation:
                return redirect(url_for('product_update', product_id=product_id_forupdation))
            elif product_id:
                product_in_app= Product.query.filter_by(id=product_id).first()
                cart_products= Cart.query.filter_by(product=product_in_app.name).all()
                for product_incart in cart_products:
                    db.session.delete(product_incart)
                db.session.delete(product_in_app)
                db.session.commit()
                flash("The product have been deleted and will be removed from the carts of all the users")
                return redirect('/admin') 
            elif category_id:
                category=Category.query.filter_by(id=category_id).first()
                products_incategory= Product.query.filter_by(category=category.name).all()
                for product in products_incategory:
                    db.session.delete(product)
                    product_incart= Cart.query.filter_by(product=product.name).all()
                    for cart_product in product_incart:
                        db.session.delete(cart_product)
                db.session.delete(category)
                db.session.commit()
                flash("The products in this category has been removed from the app and all the user's carts aswell.")
                return redirect('/admin')        
        return render_template('admin.html', products=products, categories=categories)
    
    else:
        flash('You dont have access to the following route.')
        return redirect('/home')


## Admin route for adding a new product
@app.route('/new_product', methods=['GET','POST'])
@login_required
def add_product():
    if current_user.role=='admin':
        form= ProductForm()
        form.category.query= Category.query.all()
        product_name= form.name.data
        product_price= form.price.data
        product_stock= form.stock.data
        product_category= form.category.data
        product_unit= form.unit.data
        product_manufacturingdate= form.manufacturingdate.data
        product_expirydate= form.expirydate.data
        product= Product.query
        category= Category.query
        if form.validate_on_submit():
            product_verification= product.filter_by(name=product_name).first()
            category_verification= category.filter_by(name=product_category.name).first()

            ## Check if the product already exists
            if product_verification:
                flash('Product already exists')
                return redirect(url_for('admin'))
            
            ## Check if the category exists
            elif(not category_verification):
                flash('Category doesn\'t exists')
                return redirect(url_for('add_category'))
            else:
                if not product_expirydate:
                    new_product= Product(name= product_name, price= product_price, stock=product_stock, category= product_category.name,
                    manufacturingdate= product_manufacturingdate,
                    unit= product_unit)
                else:
                    new_product= Product(name= product_name, price= product_price, stock=product_stock, category= product_category.name,
                    manufacturingdate= product_manufacturingdate,
                    expirydate= product_expirydate, unit= product_unit)

                db.session.add(new_product)
                db.session.commit()
                flash('Added a new product')
                return redirect('/admin')
        return render_template('add_product.html', form=form)
    else: 
        flash('You dont have access to the following route.')
        return redirect('/home')


## Admin route for creating a new category
@app.route('/new_category', methods=['GET','POST'])
@login_required
def add_category():
    if current_user.role=='admin':
        form=CategoryForm()
        category_name= form.name.data
        if form.validate_on_submit():
            new_category= Category(name=category_name)
            db.session.add(new_category)
            db.session.commit()
            flash('New Category Added')
            return redirect('/admin')
        return render_template('add_category.html', form=form)
    else:
        flash('You dont have access to the following route.')
        return redirect('/home')


## Route for accessing cart for user
@app.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
    cart_products= Cart.query.filter_by(user_id=current_user.id).all()
    cart_total=0
    for product in cart_products:
        cart_total+=(product.unitprice*product.quantity)
    if request.method=='POST':
        product_id= request.form.get('remove_product')
        if product_id:
            product= Cart.query.filter_by(user_id=current_user.id, id=product_id).first()
            db.session.delete(product)
            db.session.commit()
        else:
            products= Cart.query.filter_by(user_id= current_user.id).all()
            for product in products:
                stock_product= Product.query.filter_by(name=product.product).first()
                stock_product.stock-=product.quantity
                stock_product.units_sold+=product.quantity
                customers_with_product_incart= Cart.query.filter_by(product=product.product).all()
                for customer in customers_with_product_incart:
                    if customer.quantity > stock_product.stock:
                        db.session.delete(customer)
                db.session.delete(product)
            db.session.commit()
            flash('Congratulations, your purchase has been made')
            return redirect('/home')
        return redirect('/cart')
    
    return render_template('cart.html', cart_products=cart_products, cart_total=cart_total)        


## Admin route for product updation
@app.route('/update_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def product_update(product_id):
    form= ProductUpdateForm()
    product_toupdate= Product.query.filter_by(id=product_id).first()
    if current_user.role=='admin':
        product_id=product_id
        
        if form.validate_on_submit():
            new_price= form.price.data
            new_stock= form.stock.data
            new_manufacturingdate= form.manufacturingdate.data
            new_expirydate= form.expirydate.data
            if (not new_price and not new_stock and not new_manufacturingdate and not new_expirydate):
                flash('No item was updated')
                return redirect('/admin')
            else:
                if new_price:
                    product_toupdate.price= new_price
                if new_stock:
                    product_toupdate.stock+= new_stock
                if new_manufacturingdate:
                    product_toupdate.manufacturingdate= new_manufacturingdate
                if new_expirydate:
                    product_toupdate.expirydate= new_expirydate     
                db.session.commit()
                flash('The changes have been updated')
                return redirect('/admin')

        return render_template('product_update.html', form=form, product=product_toupdate)
    else:
        flash('You dont have access to the following route.')
        return redirect('/home')
