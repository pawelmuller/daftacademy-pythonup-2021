from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World!"}


@app.get("/hello/{name}")
async def hello_name(name: str):
    return f"Hello {name}"
