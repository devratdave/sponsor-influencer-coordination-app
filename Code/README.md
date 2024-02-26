# Grocery Store App

## Welcome
## Follow these instructions to start the app and assign the admin:
### 1. For MacOS
    - Open the terminal.
    - Change to the directory your project is currently in.
    - Create a virtual environment. ("python3 -m venv <VirualEnv_Name>")
    - Activate your virtual environment. 
    ("source <VirtualEnv_Name>/bin/activate")
    - Install all the libraries required from the requirements.txt file. ("pip install -r requirements.txt")
    - After installing all the libraries, instantiate the db.
        - Start the python3 interpreter ("python3")
        - Import app and db from the app.py file in the interpreter("from app import app, db")
        - With the help of app_context() initialize the database
        ("with app.app_context():")
        - Enter the command to create all the tables in the db
        ("  db.create_all()")
        - Then exit the python interpreter by typing ctrl-d
    - Simply run your flask app ("flask run")
    - The first user will always be the admin, so the first person to signup should be the admin. An admin account can not be deleted.
    - After creating the admin, populate the 'products' and 'categories' tables with multiple products and category.
    - Youre good to go.

### 2. For Windows
    - Open the command prompt.
    - Change to the directory your project is currently in.
    - Create a virtual environment. ("python3 -m venv <VirualEnv_Name>")
    - Activate your virtual environment. 
    ("./<VirtualEnv_Name>/Scripts/activate")
    - Install all the libraries required from the requirements.txt file. ("pip install -r requirements.txt")
    - After installing all the libraries, instantiate the db.
        - Start the python3 interpreter ("python3")
        - Import app and db from the app.py file in the interpreter("from app import app, db")
        - With the help of app_context() initialize the database
        ("with app.app_context():")
        - Enter the command to create all the tables in the db
        ("  db.create_all()")
        - Then exit the python interpreter by typing ctrl-z
    - Simply run your flask app ("flask run")
    - The first user will always be the admin, so the first person to signup should be the admin. An admin account can not be deleted.
    - After creating the admin, populate the 'products' and 'categories' tables with multiple products and category.
    - Youre good to go.

