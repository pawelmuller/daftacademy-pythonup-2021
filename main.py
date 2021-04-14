from fastapi import FastAPI

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
