from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, DateField, SelectField
from wtforms.validators import DataRequired, EqualTo, Length, Email, NumberRange, Optional
from wtforms_alchemy import QuerySelectField
# Create A Search Form
class SearchForm(FlaskForm):
	searched = StringField("Searched", validators=[DataRequired()])
	submit = SubmitField("Submit")

# Create Login Form
class LoginForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired()])
	password = PasswordField("Password", validators=[DataRequired()])
	submit = SubmitField("Submit")

# Create a User Form
class UserForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	username = StringField("Username", validators=[DataRequired()])
	email = StringField("Email", validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired(), Length(8, message='Password should be atleast 8 characters')])
	password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords Must Match!')])
	submit = SubmitField("Submit")

#Create a Product Form
class ProductForm(FlaskForm):
	name= StringField('Product Name', validators=[DataRequired()])
	price= IntegerField('Product Price per Unit', validators=[DataRequired()])
	category= QuerySelectField('Product Category', validators=[DataRequired()])
	stock= IntegerField('Product Stock', validators=[DataRequired(), NumberRange(0)])
	unit= SelectField('Unit of Product', choices=[('Rs./litre'), ('Rs./kg'), ('Rs./unit')], validators=[DataRequired()])
	manufacturingdate= DateField('Manufacturing Date')
	expirydate= DateField('Expiry Date', validators=[Optional()])
	submit = SubmitField("Submit")

#Create a Category Form
class CategoryForm(FlaskForm):
	name= StringField('Category Name', validators=[DataRequired()])
	submit = SubmitField("Submit")


class ProductUpdateForm(FlaskForm):
	price= IntegerField('Price', validators=[Optional()])
	stock= IntegerField('Stock', validators=[Optional()])
	manufacturingdate= DateField('Manufacturing Date', validators=[Optional()])
	expirydate= DateField('Expiry Date', validators=[Optional()])
	submit = SubmitField("Submit")





