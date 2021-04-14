from fastapi import FastAPI, Response, Request
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
