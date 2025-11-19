from typing import List
from fastapi import APIRouter, HTTPException
from ..db import get_connection
from ..schemas import Product, ProductCreate, ProductUpdate


router = APIRouter(prefix="/productos", tags=["productos"])


@router.get("", response_model=List[Product])
def list_products():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, description, price, category, available FROM products")
    rows = cur.fetchall()
    conn.close()
    return [
        Product(
            id=r["id"],
            name=r["name"],
            description=r["description"],
            price=r["price"],
            category=r["category"],
            available=bool(r["available"]),
        )
        for r in rows
    ]


@router.get("/{product_id}", response_model=Product)
def get_product(product_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, description, price, category, available FROM products WHERE id = ?",
        (product_id,),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return Product(
        id=row["id"],
        name=row["name"],
        description=row["description"],
        price=row["price"],
        category=row["category"],
        available=bool(row["available"]),
    )


@router.post("", response_model=Product, status_code=201)
def create_product(payload: ProductCreate):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO products(name, description, price, category, available) VALUES(?,?,?,?,?)",
        (
            payload.name,
            payload.description,
            payload.price,
            payload.category,
            1 if payload.available else 0,
        ),
    )
    product_id = cur.lastrowid
    conn.commit()
    conn.close()
    return get_product(product_id)


@router.put("/{product_id}", response_model=Product)
def update_product(product_id: int, payload: ProductUpdate):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    name = payload.name if payload.name is not None else row["name"]
    description = (
        payload.description if payload.description is not None else row["description"]
    )
    price = payload.price if payload.price is not None else row["price"]
    category = payload.category if payload.category is not None else row["category"]
    available = (
        1 if payload.available else 0 if payload.available is not None else row["available"]
    )

    cur.execute(
        "UPDATE products SET name=?, description=?, price=?, category=?, available=? WHERE id=?",
        (name, description, price, category, available, product_id),
    )
    conn.commit()
    conn.close()
    return get_product(product_id)


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id=?", (product_id,))
    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    conn.commit()
    conn.close()
    return None