from fastapi import FastAPI, Response
from hashlib import sha512

app = FastAPI()
app.counter = 0


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
async def method_get_return():
    return {"method": "GET"}


@app.put("/method")
async def method_put_return():
    return {"method": "PUT"}


@app.options("/method")
async def method_options_return():
    return {"method": "OPTIONS"}


@app.delete("/method")
async def method_delete_return():
    return {"method": "DELETE"}


@app.post("/method", status_code=201)
async def method_post_return():
    return {"method": "POST"}


@app.get("/auth", status_code=401)
async def method_post_return(password: str, password_hash: str, response: Response):
    if len(password) != 0 and len(password_hash) != 0:
        true_password_hash = sha512(str(password).encode('UTF-8')).hexdigest()
        if true_password_hash == password_hash:
            response.status_code = 204
