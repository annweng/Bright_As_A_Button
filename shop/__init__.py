from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail, Message


app = Flask(__name__)
app.config['SECRET_KEY'] = '601c38066f48d18decb220b4c55c28d4acd0fb4f4722dc29'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://c21018878:AnnwenGammonPage1@csmysql.cs.cf.ac.uk:3306/c21018878_coursework'

db = SQLAlchemy(app)
mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = '/login'

# security features
login_manager.session_protection = "strong"
app.config["SESSION_PERMANENT"] = False

# mail configurations
# https://github.com/mattupstate/flask-mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'brightasabutton.wa@gmail.com'
app.config['MAIL_PASSWORD'] = 'brightasabutton'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)


from shop import routes

from flask_admin import Admin
from shop.views import AdminView
from shop.models import User, Product, Review, Wishlist

admin = Admin(app, name='Admin panel', template_mode='bootstrap3')
admin.add_view(AdminView(User, db.session))
admin.add_view(AdminView(Product, db.session))
admin.add_view(AdminView(Review, db.session))
admin.add_view(AdminView(Wishlist, db.session))
