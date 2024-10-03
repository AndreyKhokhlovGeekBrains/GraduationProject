# form handling routes
from fastapi import APIRouter, Request, Form, Response, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from cookie.jwt import create_token, decode_token
from app.schemas import UserIn
from pydantic import EmailStr
from app.crud import create_user, get_user_by_login_data
import httpx
# import bcrypt
from datetime import datetime

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/")
async def html_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/form/")
async def form(request: Request):
    return templates.TemplateResponse("input_form.html", {"request": request})


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

        # Call the create_user function
        await create_user(user_in)
        # print(f"Created user: {created_user}")

        # Redirect to the home page or another page after successful submission
        return RedirectResponse(url="/", status_code=303)
        # Or redirect to a page showing the new user's details
        # return RedirectResponse(url=f"/user/{created_user['id']}", status_code=303)

    except ValueError as e:
        # Handle errors such as incorrect age, birthdate, or missing data
        return templates.TemplateResponse("input_form.html",
                                          {"request": request, "error": f'Ошибка валидации данных: {str(e)}'})

    except Exception as e:
        return templates.TemplateResponse("input_form.html", {"request": request, "error": f'Ошибка: {str(e)}'})

@router.get("/login/")
async def login_page(request: Request):
    return templates.TemplateResponse("login_form.html", {"request": request})

@router.post("/login/")
async def login_user(request: Request):
    form_data = await request.form()
    email = form_data["email"]
    password = form_data["password"]
    current_user = await get_user_by_login_data(email=email, password=password)
    user_id = current_user["id"]
    user_email = current_user["email"]
    username = current_user["name"]
    token = create_token(user_id=user_id, user_email=user_email, username=username)
    print(token)
    response = Response(content="Login successful!")
    response.set_cookie(key="JWT", value=token)
    return response

@router.get("/test_confident1/")
async def confident1(request: Request):
    token = request.cookies.get("JWT")
    if token:
        return {"test_confident1": True}
    return {"test_confident1": False}
