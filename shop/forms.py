from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp, InputRequired, NumberRange
from shop.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Regexp('^.{6,8}$', message='Your password should be between 6 and 8 characters long')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email is already associated with an account.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class ReviewForm(FlaskForm):
    review = StringField('Review', validators=[InputRequired()])
    submit = SubmitField('Post review')


class ShippingForm(FlaskForm):
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    phone = StringField('Phone', validators=[InputRequired()])
    address = StringField('Address', validators=[InputRequired()])
    city = StringField('City', validators=[InputRequired(), Regexp('^[a-zA-Z][A-Za-z\s]*$',  message='invalid city')])
    postcode = StringField('Postcode', validators=[InputRequired(), Regexp('^[a-zA-Z]{1,2}\d[A-Za-z\d]?\s*\d[A-Za-z]{2}$', message='invalid postcode')])


class CheckoutForm(FlaskForm):
    name = StringField("Cardholder's name", validators=[InputRequired(), Regexp('^[a-zA-Z][A-Za-z\s]*$', message='invalid name')])
    number = StringField('Card Number', validators=[InputRequired(), Regexp('^([0-9]{4}[- ]?){3}[0-9]{4}$', message='invalid card number')])
    month = IntegerField('Expiry Date', validators=[InputRequired(), NumberRange(min=1, max=12, message='invalid month')])
    year = IntegerField(validators=[InputRequired(), NumberRange(min=21, message='This card has expired')])
    code = StringField('Security Code', validators=[InputRequired(), Regexp('^[0-9]{3,4}$')])
