from fastapi import FastAPI, Response, Request, status, Depends, Cookie
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from hashlib import sha512
from typing import Optional
from pydantic import BaseModel
from datetime import date, timedelta
import secrets

app = FastAPI()
security = HTTPBasic()

app.counter = 0
app.patient_id = 0
app.patients = []

app.login_session = None
app.login_token = None


today = date.today()


class Patient(BaseModel):
    id: Optional[int] = None
    name: str
    surname: str
    register_date: Optional[str] = None
    vaccination_date: Optional[str] = None


@app.get("/")
def root():
    return {"message": "Hello world!"}


@app.get("/hello", response_class=HTMLResponse)
async def hello():
    return f"<h1>Hello! Today date is {today}</h1>"


@app.get("/hello/{name}")
async def hello_name(name: str):
    return f"Hello {name}"


@app.get("/counter")
async def counter():
    app.counter += 1
    return app.counter


@app.get("/method")
@app.put("/method")
@app.options("/method")
@app.delete("/method")
@app.post("/method", status_code=status.HTTP_201_CREATED)
async def method_get_return(request: Request):
    return {"method": f"{request.method}"}


@app.get("/auth", status_code=status.HTTP_401_UNAUTHORIZED)
async def method_post_return(password: str = None, password_hash: str = None, *, response: Response):
    if password is None or password_hash is None or len(password) == 0 or len(password_hash) == 0:
        response.status_code = status.HTTP_401_UNAUTHORIZED
    else:
        true_password_hash = sha512(str(password).encode('UTF-8')).hexdigest()
        if true_password_hash == password_hash:
            response.status_code = status.HTTP_204_NO_CONTENT


@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register_for_vaccination(patient: Patient):
    app.patient_id += 1
    letters_count = 0
    for letter in patient.name + patient.surname:
        if letter.isalpha():
            letters_count += 1
    vaccination_date = today + timedelta(days=letters_count)

    patient.id = app.patient_id
    patient.register_date = f'{today}'
    patient.vaccination_date = f'{vaccination_date}'
    app.patients.append(patient)
    return patient


@app.get("/patient/{patient_id}")
async def get_patient(patient_id: Optional[int] = None, *, response: Response):
    if patient_id > len(app.patients):
        response.status_code = status.HTTP_404_NOT_FOUND
        return
    elif patient_id < 1:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return
    else:
        patient = app.patients[patient_id - 1]
        response.status_code = status.HTTP_200_OK
        return patient


@app.post("/login_session", status_code=status.HTTP_201_CREATED)
async def login_session(credentials: HTTPBasicCredentials = Depends(security), *, response: Response):
    correct_username = secrets.compare_digest(credentials.username, "4dm1n")
    correct_password = secrets.compare_digest(credentials.password, "NotSoSecurePa$$")

    if correct_username and correct_password:
        app.login_session = sha512(f"{today}+{credentials.username}+{credentials.password}".encode()).hexdigest()
        response.set_cookie(key="session_token", value=app.login_session)
        return {"message": "Welcome!"}
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Wrong username or password!"}


@app.post("/login_token", status_code=status.HTTP_201_CREATED)
async def login_token(credentials: HTTPBasicCredentials = Depends(security), *, response: Response):
    correct_username = secrets.compare_digest(credentials.username, "4dm1n")
    correct_password = secrets.compare_digest(credentials.password, "NotSoSecurePa$$")

    if correct_username and correct_password:
        app.login_token = sha512(f"{today}+{credentials.username}+{credentials.password}".encode()).hexdigest()
        return {"token": app.login_token}
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Wrong username or password!"}


def welcome_response(response_format: str):
    if response_format == "html":
        html_content = "<h1>Welcome!</h1>"
        return HTMLResponse(content=html_content)
    elif response_format == "json":
        json_content = {"message": "Welcome!"}
        return JSONResponse(content=json_content)
    else:
        plain_content = "Welcome!"
        return PlainTextResponse(content=plain_content)


@app.get("/welcome_session", status_code=status.HTTP_200_OK)
async def welcome_session(format: Optional[str] = '', session_token: Optional[str] = Cookie(None), *, response: Response):
    if session_token == app.login_session:
        return welcome_response(format)
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "No session"}
