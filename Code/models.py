from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    __tablename__='users'
    id= db.Column(db.Integer, primary_key=True)
    fullname= db.Column(db.String, nullable=False)
    username= db.Column(db.String, nullable= False, unique= True)
    email= db.Column(db.String, nullable= False, unique= True)
    password= db.Column(db.String, nullable= False)
    role= db.Column(db.String, default='user')


class Category(db.Model):
    __tablename__='categories'
    id= db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String, nullable=False, unique= True)

    def __str__(self) -> str:
        return self.name 


class Product(db.Model):
    __tablename__='products'
    id= db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String, nullable=False, unique= True)
    price= db.Column(db.Integer, nullable=False)
    stock= db.Column(db.Integer, nullable=False)
    manufacturingdate= db.Column(db.DateTime, nullable= True)
    expirydate= db.Column(db.DateTime, nullable= True)
    unit= db.Column(db.String, nullable= False)
    category= db.Column(db.String, nullable= False)
    units_sold= db.Column(db.Integer, default=0)


class Cart(db.Model):
    __tablename__='cart'
    id= db.Column(db.Integer, primary_key=True)
    user_id= db.Column(db.Integer, nullable=False)
    product= db.Column(db.String)
    quantity= db.Column(db.Integer)
    unitprice= db.Column(db.Integer)
    unit= db.Column(db.String)