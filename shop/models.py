from datetime import datetime
from shop import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Wishlist(db.Model):
    wishlist_id = db.Column(db.Integer, primary_key=True)
    shoppers_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    def __repr__(self):
        return f"Wishlist('{self.wishlist_id}', '{self.shoppers_id}', '{self.item_id}' )"

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    size = db.Column(db.String(5), nullable=False)
    colour = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(40), nullable=False, default='default.jpg')
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    wishlist = db.relationship('Wishlist', backref='product', lazy=True)

    def __repr__(self):
        return f"Product('{self.name}', '{self.price}', '{self.description}')"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    product = db.relationship('Product', backref='user', lazy=True)
    review = db.relationship('Review', backref='user', lazy=True)
    wishlist = db.relationship('Wishlist', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('review.id'), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent = db.relationship('Review', backref='review_parent', remote_side=id, lazy=True)

    def __repr__(self):
        return f"Product('{self.date}', '{self.content}')"
