from fastapi import APIRouter, status, Response, HTTPException
from typing import Optional
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


@database.get("/products/{index}")
async def get_products(response: Response, index: int):
    product = database.connection.execute(
        "SELECT ProductID, ProductName FROM Products WHERE ProductID = (?)", (index,)).fetchone()
    if product is not None:
        response.status_code = status.HTTP_200_OK
        return {"id": product[0], "name": product[1]}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No product with given id")


@database.get("/employees")
async def get_employees(response: Response,
                        limit: Optional[int] = None, offset: Optional[int] = None, order: str = 'id'):
    translation = {
        "id": "EmployeeID",
        "first_name": "FirstName",
        "last_name": "LastName",
        "city": "City"
    }
    try:
        order = translation[order]
    except KeyError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"You can order only using: {translation.keys()}")

    employees = database.connection.execute(
        f"""
        SELECT EmployeeID, LastName, FirstName, City FROM Employees ORDER BY {order}
        {f" LIMIT {limit}" if limit else ""}{f" OFFSET {offset}" if offset else ""}
        """).fetchall()

    response.status_code = status.HTTP_200_OK
    response_employees = [{"id": index, "last_name": last_name, "first_name": first_name, "city": city}
                          for index, last_name, first_name, city in employees]

    return {"employees": response_employees}


@database.get("/products_extended", status_code=status.HTTP_200_OK)
async def get_products_extended():
    products = database.connection.execute(
        """
        SELECT ProductID, ProductName, C.CategoryName, S.CompanyName
        FROM Products
        JOIN Categories C on Products.CategoryID = C.CategoryID
        JOIN Suppliers S on Products.SupplierID = S.SupplierID
        ORDER BY ProductID
        """).fetchall()

    response_products = [{"id": index, "name": name, "category": category, "supplier": supplier}
                         for index, name, category, supplier in products]

    return {"products_extended": response_products}
