# form handling routes
from fastapi import APIRouter, Request, Form, Response, Depends, HTTPException, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi import APIRouter, Request, Form, Response, Depends, Body
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from fastapi.exceptions import HTTPException
from fastapi.staticfiles import StaticFiles

from cart.redis_client import redis_get_unique_item
from cookie.jwt import create_token, decode_token
from app.schemas import UserIn, NewsletterIn, TokenIn, ItemIn, GenderCategory
from pydantic import EmailStr
from app.crud import (create_user, get_user_by_login_data, add_token_to_blacklist,
                      add_newsletter_mail, add_item, load_featured_items, get_items_by_category, get_all_items)
import shutil
from app.schemas import UserIn, TokenIn
from pydantic import EmailStr, BaseModel
from app.crud import create_user, get_user_by_login_data, add_token_to_blacklist, get_token
import httpx
# import bcrypt
from datetime import datetime

router = APIRouter()

templates = Jinja2Templates(directory="templates")

count = 0


@router.get("/all")
async def get_all(request: Request):
    items_in = await get_all_items()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "featured_items": items_in,
        "count": count,
        "show_all_items": True
    })


@router.get("/category/{gender}")
async def get_items_by_gender(request: Request, gender: str):
    items_in = await get_items_by_category(gender)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "featured_items": items_in,
        "count": count,
        "gender": gender,
        "item_type": None
        })


@router.get("/category/{gender}/{item_type}")
async def get_items(request: Request, gender: str, item_type: str):
    items_in = await get_items_by_category(gender, item_type)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "featured_items": items_in,
        "count": count,
        "gender": gender,
        "item_type": item_type
    })

router.mount("/static", StaticFiles(directory="static"), name="static")


def verify_password(stored_password: str, input_password: str) -> bool:
    # Хеширование входящего пароля
    hashed_input_password = hash_password(input_password)

    # Сравнение хешей
    return hashed_input_password == stored_password

@router.get("/")
async def html_index(request: Request):
    count = 0
    token = request.cookies.get("JWT")

    if token:
        decoded_token = decode_token(token)
        user_id = decoded_token.id
        count = redis_get_unique_item(user_id)
    featured_items = await load_featured_items()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "count": count,
        "featured_items": featured_items,
        "show_all_items": False
    })


@router.get("/form/")
async def form(request: Request):
    count = 0
    token = request.cookies.get("JWT")

    if token:
        decoded_token = decode_token(token)
        user_id = decoded_token.id
        count = redis_get_unique_item(user_id)

    return templates.TemplateResponse("input_form.html", {"request": request, "count": count})


@router.post("/form/")
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
        # hashed_password = hash_password(input_password)
        # input_password_hashed = bcrypt.hashpw(input_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_in = UserIn(
            name=input_name,
            email=input_email,
            password=input_password,
            # password=input_password_hashed,
            age=input_age,
            birthdate=birthdate,
            phone=input_phone,
            agreement=True if input_checkbox == 'on' else False
        )
        # Удалить этот коментарий1
        # Call the create_user function
        await create_user(user_in)
        print(f"Created user: {user_in}")

        # Redirect to the home page or another page after successful submission
        return RedirectResponse(url="/", status_code=303)
        # return RedirectResponse(url=f"/user/{created_user['id']}", status_code=303)

    except ValueError as e:

        return templates.TemplateResponse("input_form.html",
                                          {"request": request, "error": f'Ошибка валидации данных: {str(e)}'})

    except Exception as e:
        return templates.TemplateResponse("input_form.html", {"request": request, "error": f'Ошибка: {str(e)}'})


@router.get("/login/")
async def login_page(request: Request):
    count = 0
    token = request.cookies.get("JWT")

    if token:
        decoded_token = decode_token(token)
        user_id = decoded_token.id
        count = redis_get_unique_item(user_id)
    return templates.TemplateResponse("login_form.html", {"request": request, "count": count})


@router.post("/login/")
async def login_user(request: Request):
    form_data = await request.form()
    token = request.cookies.get("JWT")
    # response = Response()
    # response.delete_cookie("JWT")
    if token is not None:
        print(token)
        # response.delete_cookie("JWT")
        # await add_token_to_blacklist(token)

    try:
        email, password = form_data["email"], form_data["password"]
        print(email)
        print(password)
        # hashed_password = hash_password(password)
        current_user = await get_user_by_login_data(email=email, password=password)

        user_id = int(current_user["id"])
        user_email = str(current_user["email"])
        username = str(current_user["name"])
        token = create_token(user_id=user_id, user_email=user_email, username=username)
        print(f"Token: {token}")

        # response.set_cookie(key="JWT", value=token)
        # response.headers["Location"] = "/login&success=true"
        return RedirectResponse(url="/login?success=true", headers={"JWT": token}, status_code=303)

    except TypeError:
        return {'msg': "user not exists"}


@router.get("/logout/")
async def logout_page(request: Request):
    if request.cookies.get("JWT"):
        return templates.TemplateResponse("logout.html", {"request": request, "count": count})
    token = request.cookies.get("JWT")

    if token:
        decoded_token = decode_token(token)
        user_id = decoded_token.id
        count = redis_get_unique_item(user_id)
        return templates.TemplateResponse("logout.html", {"request": request, "count": count})
    return RedirectResponse(url="/login/")


@router.post("/logout/")
async def logout(request: Request):
    token = request.cookies.get("JWT")
    print(token)
    if token:
        response = Response(status_code=302)
        response.headers["Location"] = "http://127.0.0.1:8000/"
        token_in = TokenIn(token=token)
        response.delete_cookie("JWT")
        await add_token_to_blacklist(token_in=token_in)
        #return RedirectResponse(url="/")
        return response
    return RedirectResponse(url="/login/")



@router.get("/test_confident1/")
async def confident1(request: Request):
    token = request.cookies.get("JWT")
    if token:
        return {"test_confident1": True}
    return {"test_confident1": False}


@router.post("/subscribe")
async def subscribe(
        email: EmailStr = Form(...)
):
    newsletter_in = NewsletterIn(email=email)
    await add_newsletter_mail(newsletter_in)
    print(f"Created mail: {newsletter_in}")
    return RedirectResponse(url="/", status_code=303)
