from flask import Flask


app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret_key'

from routes import home, goods, users, cart, orders