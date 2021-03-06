import sqlite3
from typing import Optional

from fastapi import APIRouter, status, Response, HTTPException
from pydantic import BaseModel

database = APIRouter()
database.__name__ = "DataBase"


class NewCategory(BaseModel):
    name: str


@database.on_event("startup")
async def startup():
    database.connection = sqlite3.connect("Database/northwind.db")
    database.connection.text_factory = lambda b: b.decode(errors="ignore")  # Northwind specific


@database.on_event("shutdown")
async def shutdown():
    database.connection.close()


@database.get("/customers", status_code=status.HTTP_200_OK)
async def get_customers():
    customers = database.connection.execute(
        """
        SELECT CustomerID, CompanyName, Address || ' ' || PostalCode || ' ' || City || ' ' || Country
        FROM Customers
        """
    ).fetchall()
    response_customers = [{"id": index, "name": name, "full_address": address} for index, name, address in customers]
    return {"customers": response_customers}


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


def check_product_existence(product_id):
    product = database.connection.execute(
        "SELECT ProductID FROM Products WHERE ProductID = (?)", (product_id,)).fetchone()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No product with given id")


@database.get("/products/{product_id}/orders", status_code=status.HTTP_200_OK)
async def get_products_extended(product_id: int):
    check_product_existence(product_id)

    orders = database.connection.execute(
        """
        SELECT O.OrderID, C.CompanyName, OD.Quantity,
            ROUND(OD.UnitPrice * OD.Quantity - (OD.Discount * (OD.UnitPrice * OD.Quantity)), 2) as TotalPrice
        FROM Orders O
        JOIN "Order Details" OD on O.OrderID = OD.OrderID
        JOIN Customers C on O.CustomerID = C.CustomerID
        WHERE ProductID = (?)
        """, (product_id,)).fetchall()

    response_orders = [{"id": index, "customer": customer, "quantity": quantity, "total_price": total_price}
                       for index, customer, quantity, total_price in orders]

    return {"orders": response_orders}


async def check_category_existence(category_id):
    category = database.connection.execute(
        "SELECT CategoryID FROM Categories WHERE CategoryID = (?)", (category_id,)).fetchone()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No category with given id.")


@database.get("/categories", status_code=status.HTTP_200_OK)
async def get_categories():
    categories = database.connection.execute(
        "SELECT CategoryID, CategoryName FROM Categories ORDER BY CategoryID"
    ).fetchall()
    response_categories = [{"id": index, "name": name} for index, name in categories]
    return {"categories": response_categories}


@database.post("/categories", status_code=status.HTTP_201_CREATED)
async def post_categories(new_category: NewCategory):
    insert = database.connection.execute(f"INSERT INTO Categories (CategoryName) VALUES ('{new_category.name}')")
    database.connection.commit()
    return {"id": insert.lastrowid, "name": new_category.name}


@database.put("/categories/{category_index}", status_code=status.HTTP_200_OK)
async def put_categories(category: NewCategory, category_index: int):
    await check_category_existence(category_index)

    database.connection.execute(
        "UPDATE Categories SET CategoryName = ? WHERE CategoryID = ?",
        (category.name, category_index), )
    database.connection.commit()
    return {"id": category_index, "name": category.name}


@database.delete("/categories/{category_index}", status_code=status.HTTP_200_OK)
async def delete_categories(category_index: int):
    await check_category_existence(category_index)

    database.connection.execute(
        "DELETE FROM Categories WHERE CategoryID = ?",
        (category_index,))
    database.connection.commit()
    return {"deleted": 1}
