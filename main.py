from fastapi import FastAPI


def main():
    app = FastAPI()

    @app.get("/")
    def root():
        return {"message": "Hello World!"}


if __name__ == '__main__':
    main()
