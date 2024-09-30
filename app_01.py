# import httpx
from datetime import datetime
from flask import Flask, render_template, request, abort, flash, url_for, redirect
from models_01 import UserIn
from flask import Flask, render_template
from cart.redis_client import redis_backup, redis_add_to_cart,  redis_get_from_cart, redis_clear_cart
import json


# from models_02 import db, User, Post, Comment

app = Flask(__name__)
app.secret_key = b'df40bb13e3125376d80767950a4499e165f2be7c35728768f2b9e4a8a8d39675'
"""
Генерация недёжного секретного ключа
>>> import secrets
>>> secrets.token_hex()
"""
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
# db.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
# db.init_app(app)


@app.route('/')
def html_index():
    return render_template('index.html')


@app.route('/index/')
def index():
    context = {
        'title': 'Интернет магазин',
        'name': 'Харитон', }
    return render_template('index.html', **context)


# @app.errorhandler(404)
# def page_not_found(e):
#     app.logger.warning(e)
#     context = {
#         'title': 'Страница не найдена',
#         'url': request.base_url,
#     }
#     return render_template('404.html', **context), 404


@app.errorhandler(500)
def page_not_found(e):
    app.logger.error(e)
    context = {
        'title': 'Ошибка сервера',
        'url': request.base_url,
    }
    return render_template('500.html', **context), 500


@app.route('/form/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        # Extract all form data
        name = request.form.get('input-name')
        email = request.form.get('input-email')
        password = request.form.get('input-password')
        age = request.form.get('input-age')
        birthdate_str = request.form.get('input-birthdate')
        phone = request.form.get('input-phone')
        checkbox = request.form.get('input-checkbox')  # Will return 'on' if checked

        # Simple validation for name, feel free to extend validation to other fields
        if not name:
            flash('Введите имя!', 'danger')
            return redirect(url_for('form'))

        try:
            # Parse the birthdate from string to a date object
            birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d').date()

            user_in = UserIn(
                name=name,
                email=email,
                password=password,
                age=int(age),
                birthdate=birthdate,
                phone=phone,
                agreement=True if checkbox == 'on' else False
            )

            print(user_in)

        except Exception as e:
            print(e)
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
