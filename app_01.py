from flask import Flask, render_template
from redis_client import redis_backup, add_to_cart as redis_add_to_cart, get_from_cart as redis_get_from_cart
import json

# from models_02 import db, User, Post, Comment

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
# db.init_app(app)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/add_to_cart/<int:position_id>')
def add_to_cart(position_id):
    redis_add_to_cart(user_id=None, position_id=position_id)  # user_id надо сделать потом


@app.route("/get_from_cart/")
def get_from_cart():
    positions = redis_get_from_cart(user_id=None)  # user_id надо сделать потом

    json_dict = {{i + 1}: value for i, value in enumerate(positions)}

    json_string = json.dumps(json_dict)
    return json_string


@app.cli.command("init-db")
def init_db():
    # показать ошибку с неверным wsgi.py
    # db.create_all()
    print('OK')


@app.cli.command("init-redis")
def init_redis():
    redis_backup()


"""
if __name__ == '__main__':
    app.run(debug=True)
"""
