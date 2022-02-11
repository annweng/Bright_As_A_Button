from flask import render_template, url_for, request, redirect, flash, session
from shop import app, db, mail
from shop.models import User, Product, Review, Wishlist
from shop.forms import RegistrationForm, LoginForm, ReviewForm, CheckoutForm, ShippingForm   
from flask_login import login_user, logout_user, login_required, current_user, login_manager
from flask_mail import Mail, Message


@app.route("/")
@app.route("/home")
def home():
    products = Product.query.all()
    return render_template('home.html', products=products)

# filters

@app.route('/LowToHigh')
def filterLTH():
    products = Product.query.order_by(Product.price.asc()).all()
    return render_template('home.html', products=products)


@app.route('/HighToLow')
def filterHTL():
    products = Product.query.order_by(Product.price.desc()).all()
    return render_template('home.html', products=products)


@app.route('/Adults')
def filterAdults():
    products = Product.query.filter_by(size='Adult')
    return render_template('home.html', products=products)


@app.route('/Childs')
def filterChilds():
    products = Product.query.filter_by(size='Child')
    return render_template('home.html', products=products)

# pages


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/basket")
@login_required
def basket():
    if 'Basket' not in session or len(session['Basket']) <= 0:
        flash('You have nothing in your basket')
        subtotal = 0
        return render_template('basket.html', title='Shopping Basket', subtotal=subtotal)
    else:
        subtotal, BasketList = getSubtotal(session['Basket'])
        return render_template('basket.html', title='Shopping Basket', BasketList=BasketList, subtotal=subtotal)


def getSubtotal(products):
    BasketList = []
    if len(products) > 0:
        for product in products:
            productObject = Product.query.filter_by(id=product["id"]).first()
            BasketList.append([productObject, product['quantity']])
            subtotal = 0
            for item in BasketList:
                subtotal += item[0].price * item[1]
    else:
        subtotal = 0
    return subtotal, BasketList


@app.route("/checkout", methods=['POST', 'GET'])
def checkout():
    form = CheckoutForm()
    subtotal, BasketList = getSubtotal(session['Basket'])
    if form.validate_on_submit():
        flash('Payment successful!')
        session['Basket'].clear()
        return redirect(url_for('confirmation'))
    return render_template('checkout.html', title='Checkout', form=form, subtotal=subtotal)


@app.route("/shipping", methods=['POST', 'GET'])
def shipping():
    form = ShippingForm()
    if form.validate_on_submit():
        return redirect(url_for('checkout'))
    return render_template('shipping.html', title='Shipping', form=form)


@app.route("/confirmation", methods=['POST', 'GET'])
def confirmation():
    if current_user.is_authenticated:
        msg = Message('Payment Confirmation', sender='annwengammon1@gmail.com', recipients=[current_user.email])
        msg.html = """<h1>Order Confirmation</h1><br><p>Congratulations! Your order will be on it's way soon!</p>"""
        mail.send(msg)
        flash("A confirmation has been sent to your email")
    return render_template('confirmation.html', title='confirmation')


@app.route("/wishlist", methods=['POST', 'GET'])
@login_required
def wishlist():
    query = db.session.query(Wishlist.item_id, Wishlist.shoppers_id, Product).join(Product)
    products = query.all()
    wishlistList = []
    for i in products:
        if i[1] == current_user.id:
            if i[2] not in wishlistList:
                wishlistList.append(i[2])
    if len(products) == 0:
        flash('Your wishlist is empty')
    return render_template('wishlist.html', title='wishlist', products=products, wishlistList=wishlistList)

# wishlist functions


@app.route('/addWishlist', methods=['POST', 'GET'])
@login_required
def AddWishlist():
    id = request.form.get('product_id')
    product = Product.query.filter_by(id=id).first()
    db.session.add(Wishlist(item_id=product.id, shoppers_id=current_user.id))
    db.session.commit()
    return redirect(request.referrer)


@app.route('/deleteWishlist', methods=['POST', 'GET'])
@login_required
def deleteWishlist():
    id = request.form.get('product_id')
    product = Wishlist.query.filter_by(item_id=id).first()
    db.session.delete(product)
    db.session.commit()
    flash("Your item has been deleted", "Success!")
    return redirect(request.referrer)            

# basket functions


@app.route('/addBasket', methods=['POST'])
@login_required
def AddBasket():
    id = request.form.get('product_id')
    quantity = int(request.form.get('quantity'))
    product = Product.query.filter_by(id=id).first()
    if request.method == "POST":
        item = {'id': product.id, 'quantity': quantity}
        if 'Basket' in session:
            ProductIds = [x['id'] for x in session['Basket']]
            if item['id'] in ProductIds:
                session['Basket'][ProductIds.index(item['id'])]['quantity'] += item['quantity']
                session.modified = True
                return redirect(request.referrer)
            else:
                session['Basket'].append(item)
                session.modified = True
                return redirect(request.referrer)
        else:
            session['Basket'] = [item]
            return redirect(request.referrer)


@app.route('/DecreaseQuantity', methods=['POST'])
def DecreaseQuantity():
    if 'Basket' not in session or len(session['Basket']) <= 0:
        return redirect(url_for('home'))
    product_id = int(request.form["product_id"])
    session.modified = True
    for index, item in enumerate(session['Basket']):
        if item['id'] == product_id:
            if session['Basket'][index]['quantity'] > 1:
                session['Basket'][index]['quantity'] -= 1
            else:
                session['Basket'].remove(item)
    return redirect(url_for('basket'))


@app.route('/IncreaseQuantity', methods=['POST'])
def IncreaseQuantity():
    if 'Basket' not in session or len(session['Basket']) <= 0:
        return redirect(url_for('home'))
    product_id = int(request.form["product_id"])
    session.modified = True
    for index, item in enumerate(session['Basket']):
        if item['id'] == product_id:
            session['Basket'][index]['quantity'] += 1
    return redirect(url_for('basket'))


@app.route('/deleteproduct', methods=['POST'])
def deleteproduct():
    if 'Basket' not in session or len(session['Basket']) <= 0:
        return redirect(url_for('home'))
    product_id = int(request.form["product_id"])
    session.modified = True
    for item in session['Basket']:
        if item['id'] == product_id:
            session['Basket'].remove(item)
    return redirect(url_for('basket'))

# detailed product page and function

@app.route("/product/<int:product_id>")
def product(product_id):
    product = Product.query.get_or_404(product_id)
    reviews = Review.query.filter(Review.product_id == product.id)
    form = ReviewForm()
    return render_template('product.html', product=product, reviews=reviews, form=form)


@app.route('/product/<int:product_id>/review', methods=['GET', 'POST'])
@login_required
def product_review(product_id):
    product = Product.query.get_or_404(product_id)
    form = ReviewForm()
    if form.validate_on_submit():
        db.session.add(Review(content=form.review.data, product_id=product.id, author_id=current_user.id))
        db.session.commit()
        flash("Your review has been added", "Success!")
        return redirect(f'/product/{product.id}')
    reviews = Review.query.filter(Review.product_id == product.id)
    return render_template('product.html', product=product, reviews=reviews, form=form)

# Account details


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            flash('Login successful!')
            return redirect(url_for('home'))
        flash('Invalid email address or password.')
        return render_template('login.html', form=form)
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    flash('Logout successful!')
    return redirect(url_for('home'))
