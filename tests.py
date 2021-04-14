from fastapi.testclient import TestClient
from main import app
from hashlib import sha512

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
