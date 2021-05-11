from fastapi import APIRouter, status
import sqlite3


database = APIRouter()
database.__name__ = "DataBase"


@database.on_event("startup")
async def startup():
    database.connection = sqlite3.connect("Database/northwind.db")
    database.connection.text_factory = lambda b: b.decode(errors="ignore")  # Northwind specific


@database.on_event("shutdown")
async def shutdown():
    database.connection.close()
