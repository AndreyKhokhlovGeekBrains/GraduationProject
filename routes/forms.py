# form handling routes
from fastapi import APIRouter, Request, Form, Response, Depends, Body
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import HTTPException
from fastapi.staticfiles import StaticFiles

from cart.redis_client import redis_get_unique_item
from cookie.jwt import create_token, decode_token
from app.schemas import UserIn, TokenIn
from pydantic import EmailStr, BaseModel
from app.crud import create_user, get_user_by_login_data, add_token_to_blacklist, get_token
import httpx
# import bcrypt
from datetime import datetime

router = APIRouter()

templates = Jinja2Templates(directory="templates")
router.mount("/static", StaticFiles(directory="static"), name="static")

class LoginData(BaseModel):
    email: EmailStr
    password: str


@router.get("/")
async def html_index(request: Request):
    count = 0
    token = request.cookies.get("JWT")

    if token:
        decoded_token = decode_token(token)
        user_id = decoded_token.id
        count = redis_get_unique_item(user_id)
    return templates.TemplateResponse("index.html", {"request": request, "count": count})


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
        # input_age: int = Form(..., ge=1, alias="input-age", description="Age must be a positive integer"),
        input_birthdate: str = Form(..., alias="input-birthdate", description="Birthdate in YYYY-MM-DD format"),
        input_phone: str = Form(..., alias="input-phone", description="Phone number"),
        input_checkbox: str = Form(None, alias="input-checkbox")  # This will be 'on' if checked
):
    count = 0
    token = request.cookies.get("JWT")

    if token:
        decoded_token = decode_token(token)
        user_id = decoded_token.id
        count = redis_get_unique_item(user_id)
    # Simple validation for name, feel free to extend validation to other fields
    if not input_name:
        return templates.TemplateResponse("input_form.html", {"request": request, "error": "Введите имя!",
                                                              "count": count})

    try:
        # Parse the birthdate from string to a date object
        birthdate = datetime.strptime(input_birthdate, '%Y-%m-%d').date()

        # input_password_hashed = bcrypt.hashpw(input_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_in = UserIn(
            name=input_name,
            email=input_email,
            password=input_password,
            # password=input_password_hashed,
            birthdate=birthdate,
            phone=input_phone,
            agreement=True if input_checkbox == 'on' else False
        )

        # Call the create_user function
        result = await create_user(user_in)
        print(f"Created user: {user_in}")
        print(f"Result: {result}")
        # Redirect to the home page or another page after successful submission
        return RedirectResponse(url="/", status_code=303)
        # return templates.TemplateResponse("input_form.html",
                                          #{"request": request,
                                           #"count": count})
        # Or redirect to a page showing the new user's details
        # return RedirectResponse(url=f"/user/{created_user['id']}", status_code=303)

    except ValueError as e:
        # Handle errors such as incorrect age, birthdate, or missing data
        return templates.TemplateResponse("input_form.html",
                                          {"request": request, "error": f'Ошибка валидации данных: {str(e)}',
                                           "count": count})

    except Exception as e:
        return templates.TemplateResponse("input_form.html", {"request": request, "error": f'Ошибка: {str(e)}',
                                                              "count": count})


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
    response = Response()
    count = 0

    if token:
        decoded_token = decode_token(token)
        user_id = decoded_token.id
        count = redis_get_unique_item(user_id)
        response.delete_cookie("JWT")
        # token_in = TokenIn(token=token)
        # current_token = await get_token(token)
        # if not current_token:
            # await add_token_to_blacklist(token_in)

    try:
        email, password = form_data.get("email"), form_data.get("password")
        current_user = await get_user_by_login_data(email=email, password=password)
        if current_user:
            user_id, user_email, username = current_user["id"], current_user["email"], current_user["name"]
            token = create_token(user_id=user_id, user_email=user_email, username=username)
            response.set_cookie(key="JWT", value=token)
            response.status_code = 200
            return RedirectResponse(url="/", status_code=303, headers={"JWT": token})
    except Exception as e:
        print(e)
        return RedirectResponse(url="/login/", status_code=303)


@router.get("/logout/")
async def logout_page(request: Request):
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
