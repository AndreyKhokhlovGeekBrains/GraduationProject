import json


import databases
import sqlalchemy
from fastapi import FastAPI, Request, Form, HTTPException, Depends, status, Response, routing
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr, Field, constr
from typing import List
from datetime import datetime, date
import httpx
from cart.redis_client import redis_get_from_cart
from jwt import create_token, decode_token

DATABASE_URL = "sqlite:///mydatabase.db"
# DATABASE_URL = "postgresql://user:password@localhost/dbname"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(32)),
    sqlalchemy.Column("email", sqlalchemy.String(128)),
    sqlalchemy.Column("password", sqlalchemy.String(255)),
    sqlalchemy.Column("age", sqlalchemy.Integer),
    sqlalchemy.Column("birthdate", sqlalchemy.Date),
    sqlalchemy.Column("phone", sqlalchemy.String(20)),
    sqlalchemy.Column("agreement", sqlalchemy.Boolean),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, default=datetime.now),
)

engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata.create_all(engine)

# Initialize FastAPI app
app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create an instance of Jinja2Templates with the directory where your templates are stored
templates = Jinja2Templates(directory="templates")


class UserIn(BaseModel):
    name: constr(max_length=32) = Field(..., description="Name of the user")
    email: constr(max_length=128) = Field(..., description="Email of the user")
    password: constr(min_length=8, max_length=255) = Field(..., description="Password with minimum 8 characters")  # Added min_length for security
    age: int = Field(None, gt=0, description="Age must be a positive integer")  # Age should be greater than 0
    birthdate: date = Field(..., description="Birthdate in YYYY-MM-DD format")
    phone: str = Field(..., pattern=r'^\+?\d{7,20}$', description="Phone number with 7-20 digits, optional + for international format")
    agreement: bool = Field(None, description="Check box")


class User(BaseModel):
    id: int
    name: str = Field(max_length=32)
    email: str = Field(max_length=128)


@app.get("/", response_class=HTMLResponse)
async def html_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/get_cart/")
def get_from_cart(request: Request):
    token = request.cookies.get("token")
    decoded_token = decode_token(token)
    token_query = decoded_token.model_dump()
    try:
        positions = redis_get_from_cart(user_id=token_query["id"])
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


@app.get("/cart/", response_class=HTMLResponse)
async def get_cart(request: Request):
    context = {
        "title": "Ваша корзина",
        "content": json.loads(response)
    }
    return templates.TemplateResponse("cart.html", **context)


@app.get("/form/")
async def form(request: Request):
    return templates.TemplateResponse("input_form.html", {"request": request})

@app.post("/form/")
async def submit_form(
        request: Request,
        input_name: str = Form(..., alias="input-name", description="Name of the user"),
        input_email: EmailStr = Form(..., alias="input-email", description="Email of the user"),
        input_password: str = Form(..., alias="input-password", description="Password of the user"),
        input_age: int = Form(..., ge=1, alias="input-age", description="Age must be a positive integer"),
        input_birthdate: str = Form(..., alias="input-birthdate", description="Birthdate in YYYY-MM-DD format"),
        input_phone: str = Form(..., alias="input-phone", description="Phone number"),
        input_checkbox: str = Form(None, alias="input-checkbox")  # This will be 'on' if checked
):
    # Simple validation for name, feel free to extend validation to other fields
    if not input_name:
        return templates.TemplateResponse("input_form.html", {"request": request, "error": "Введите имя!"})

    try:
        # Parse the birthdate from string to a date object
        birthdate = datetime.strptime(input_birthdate, '%Y-%m-%d').date()

        user_in = UserIn(
            name=input_name,
            email=input_email,
            password=input_password,
            age=input_age,
            birthdate=birthdate,
            phone=input_phone,
            agreement=True if input_checkbox == 'on' else False
        )
        print(f"User In: \n {user_in}")

        # Convert the date to string in YYYY-MM-DD format
        user_data = user_in.model_dump()
        print(f"User  data: \n {user_data}")

        # Create a new user
        query = users.insert().values(**user_data)
        await database.execute(query)

        return RedirectResponse("/form/", status_code=301)

    except ValueError as e:
        # Handle errors such as incorrect age, birthdate, or missing data
        return templates.TemplateResponse("input_form.html", {"request": request, "error": f'Ошибка валидации данных: {str(e)}'})


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

"""
@app.post("/user_create/", response_model=User)
async def create_user(user: UserIn):
    # query = users.insert().values(name=user.name, email=user.email)
    query = users.insert().values(**user)
    last_record_id = await database.execute(query) # The database.execute() method in FastAPI with the databases library returns the last inserted primary key value.
    return {**user.model_dump(), "id": last_record_id}
"""

@app.get("/users/", response_model=List[User])
async def read_users(skip: int = 0, limit: int = 10):
    query = users.select().offset(skip).limit(limit)
    return await database.fetch_all(query)


@app.get("/read_user/{user_id: int}", response_model=User)
async def read_user(user_id: int):
    query = users.select().where(users.c.id == user_id)
    return await database.fetch_one(query)


@app.put("/users/", response_model=User)
async def update_user(new_user: UserIn, request: Request):
    if token:
        query = users.update().where(users.c.id == user_id).values(**new_user.model_dump())
        update_jwt(new_user, user_id, token)
        await database.execute(query)
    return {**new_user.model_dump(), "id": user_id}


@app.delete("/users/")
async def delete_user(request: Request):
    print(type(user_id))
    if token:
        query = users.delete().where(users.c.id == user_id)
        await database.execute(query)
        revoke_token(token)
    return {'message': 'User deleted'}

@app.get("/login/")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login/")
async def login_user(request: Request):
    form_data = await request.form()
    form_email = form_data["email"]
    form_password = form_data["password"]

    query = users.select().where(users.c.email == form_email, users.c.password == form_password)
    user = await database.fetch_one(query)
    user = dict(user)
    if user:
        token = create_token(user_id=user["id"], user_email=user["name"], username=user["email"])
        response = Response(status_code=200, headers={"authorization": f"Bearer: {token}"})
        response.set_cookie("token", token)
        return response

# pip install databases[aiosqlite]
# pip install uvicorn
# pip install pydantic[email]
# uvicorn models_01:app --reload
