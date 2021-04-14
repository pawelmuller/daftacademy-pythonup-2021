import string
from fastapi import FastAPI, Response, Request
from hashlib import sha512
from typing import Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

app = FastAPI()
app.counter = 0
app.patient_id = 0
app.patients = []


class Patient(BaseModel):
    id: Optional[int] = None
    name: str
    surname: str
    register_date: Optional[str] = None
    vaccination_date: Optional[str] = None


@app.get("/")
def root():
    return {"message": "Hello world!"}


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
@app.post("/method", status_code=201)
async def method_get_return(request: Request):
    return {"method": f"{request.method}"}


@app.get("/auth", status_code=401)
async def method_post_return(password: str = None, password_hash: str = None, *, response: Response):
    if password is None or password_hash is None:
        response.status_code = 401
    elif len(password) != 0 and len(password_hash) != 0:
        true_password_hash = sha512(str(password).encode('UTF-8')).hexdigest()
        if true_password_hash == password_hash:
            response.status_code = 204


@app.post("/register", status_code=201)
async def register_for_vaccination(patient: Patient):
    today = datetime.now()
    app.patient_id += 1

    patient.id = app.patient_id
    patient.register_date = f'{today.year}-{today.month:02}-{today.day:02}'

    name_surname = ''
    for name in (patient.name, patient.surname):
        for letter in name:
            if letter in string.ascii_letters:
                name_surname += letter

    difference = len(name_surname)
    vaccination_date = today + timedelta(days=difference)
    patient.vaccination_date = f'{vaccination_date.year}-{vaccination_date.month:02}-{vaccination_date.day:02}'
    app.patients.append(patient)
    return patient


@app.get("/patient/{patient_id}")
async def get_patient(patient_id: Optional[int] = None, *, response: Response):
    if patient_id > len(app.patients):
        response.status_code = 404
        return
    elif patient_id < 1:
        response.status_code = 400
        return
    else:
        patient = app.patients[patient_id - 1]
        response.status_code = 200
        return patient
