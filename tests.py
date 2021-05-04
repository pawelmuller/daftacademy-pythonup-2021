import pytest
from fastapi.testclient import TestClient
from main import app
from hashlib import sha512
from datetime import datetime, timedelta

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello world!"}


def test_hello_name():
    name = 'Pawel'
    response = client.get(f"/hello/{name}")
    assert response.status_code == 200
    assert response.text == f'"Hello {name}"'


def test_counter():
    response = client.get(f"/counter")
    assert response.status_code == 200
    assert response.text == "1"

    response = client.get(f"/counter")
    assert response.status_code == 200
    assert response.text == "2"


def test_method_return():
    response = client.get(f"/method")
    assert response.status_code == 200
    assert response.json() == {"method": "GET"}

    response = client.put(f"/method")
    assert response.status_code == 200
    assert response.json() == {"method": "PUT"}

    response = client.options(f"/method")
    assert response.status_code == 200
    assert response.json() == {"method": "OPTIONS"}

    response = client.delete(f"/method")
    assert response.status_code == 200
    assert response.json() == {"method": "DELETE"}

    response = client.post(f"/method")
    assert response.status_code == 201
    assert response.json() == {"method": "POST"}


def test_auth():
    passwords = ['pass', 778866123, 'pear', 'bearDrunkBeer']
    for password in passwords:
        password_hash = sha512(str(password).encode('UTF-8')).hexdigest()
        response = client.get(f"/auth?password={password}&password_hash={password_hash}")
        assert response.status_code == 204

    for password in passwords:
        password_hash = 'wrongHashActually'
        response = client.get(f"/auth?password={password}&password_hash={password_hash}")
        assert response.status_code == 401

    response = client.get(f"/auth?password=&password_hash='something'")
    assert response.status_code == 401

    response = client.get(f"/auth?password='something&password_hash=")
    assert response.status_code == 401

    response = client.get(f"/auth")
    assert response.status_code == 401


@pytest.mark.parametrize("index,name,surname,days",
                         [(1, "Jan", "Kowalski", 11),
                          (2, "Artur", "Nawalka", 12),
                          (3, "Bogdan", "Nowacki", 13),
                          (4, "Aleksander", "Multiinstrumentalista", 31),
                          (5, "Olgab 432 mm", "Orangut4n", 15),
                          (6, "Żarłoczny", "Abażurå", 16)])
def test_vaccinate(index, name, surname, days):
    today = datetime.now()
    vaccination_date = today + timedelta(days=days)

    json_to_post = {
        "name": name,
        "surname": surname
    }
    resp = {
       "id": index,
       "name": name,
       "surname": surname,
       "register_date": f'{today.year}-{today.month:02}-{today.day:02}',
       "vaccination_date": f'{vaccination_date.year}-{vaccination_date.month:02}-{vaccination_date.day:02}'
    }
    response = client.post(f"/register", json=json_to_post)
    assert response.json() == resp
    assert response.status_code == 201


def test_get_patient():
    response = client.get(f"/patient/-1")
    assert response.status_code == 400

    response = client.get(f"/patient/2")
    resp = response.json()
    assert resp["name"] == "Artur"
    assert response.status_code == 200

    response = client.get(f"/patient/300")
    assert response.status_code == 404
