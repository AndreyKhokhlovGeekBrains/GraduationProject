from flask import Flask, render_template
from cart.redis_client import redis_backup, redis_add_to_cart,  redis_get_from_cart, redis_clear_cart
import json


# from models_02 import db, User, Post, Comment

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
# db.init_app(app)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/add_to_cart/<int:user_id>/<int:position_id>/<int:amount>')
def add_to_cart(user_id, position_id, amount):
    try:
        redis_add_to_cart(user_id=user_id, position_id=position_id, amount=amount)  # user_id надо сделать потом
    except Exception as e:
        return {"status": 400, "exception": e}
    return {"status": 200}


@app.route("/get_cart/<int:user_id>")
def get_from_cart(user_id):
    try:
        positions = redis_get_from_cart(user_id=user_id)  # user_id надо сделать потом
        print(positions)
        # Create a dictionary with the desired structure
        json_dict = {}
        for i, (item_id, quantity) in enumerate(positions.items()):
            json_dict[str(i + 1)] = {item_id: quantity}

        if json_dict:
            json_string = json.dumps(json_dict)
            return json_string

    except Exception as e:
        return {"status": 200, "content": "Cart is empty :(", "error": str(e)}


@app.route("/clear_cart/<int:user_id>")
def clear_cart(user_id):
    redis_clear_cart(user_id=user_id)
    return {"status": 200}

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
