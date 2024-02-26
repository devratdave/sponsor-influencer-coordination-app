from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app= Flask(__name__)
app.config['SECRET_KEY']= 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///groceryStore.db'
db=SQLAlchemy(app)
login_manager= LoginManager(app)
login_manager.init_app(app)

import routes

if __name__== '__main__':
    app.run(debug=True)