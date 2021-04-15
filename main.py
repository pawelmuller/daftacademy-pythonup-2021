from fastapi import FastAPI, Response, Request
from hashlib import sha512
from typing import Optional
from pydantic import BaseModel
from datetime import date, timedelta

app = FastAPI()
app.counter = 0
app.patient_id = 0
app.patients = []

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
    if password is None or password_hash is None or len(password) == 0 or len(password_hash) == 0:
        response.status_code = 401
    else:
        true_password_hash = sha512(str(password).encode('UTF-8')).hexdigest()
        if true_password_hash == password_hash:
            response.status_code = 204


@app.post("/register", status_code=201)
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
        response.status_code = 404
        return
    elif patient_id < 1:
        response.status_code = 400
        return
    else:
        patient = app.patients[patient_id - 1]
        response.status_code = 200
        return patient
