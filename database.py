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


@database.get("/categories", status_code=status.HTTP_200_OK)
async def get_categories():
    categories = database.connection.execute(
        "SELECT CategoryID, CategoryName FROM Categories ORDER BY CategoryID"
                                             ).fetchall()
    categories = [{"id": index, "name": name} for index, name in categories]
    return {"categories": categories}


@database.get("/customers", status_code=status.HTTP_200_OK)
async def get_customers():
    customers = database.connection.execute(
        """
        SELECT CustomerID, CompanyName, Address || ' ' || PostalCode || ' ' || City || ' ' || Country
        FROM Customers
        """
                                             ).fetchall()
    customers = [{"id": index, "name": name, "full_address": address} for index, name, address in customers]
    return {"customers": customers}
