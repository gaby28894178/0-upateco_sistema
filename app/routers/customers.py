from typing import List
from fastapi import APIRouter, HTTPException
from ..db import get_connection
from ..schemas import Customer, CustomerCreate, CustomerUpdate


router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.get("", response_model=List[Customer])
def list_customers():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, phone, address FROM customers")
    rows = cur.fetchall()
    conn.close()
    return [
        Customer(id=r["id"], name=r["name"], phone=r["phone"], address=r["address"]) for r in rows
    ]


@router.get("/{customer_id}", response_model=Customer)
def get_customer(customer_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, phone, address FROM customers WHERE id=?", (customer_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return Customer(id=row["id"], name=row["name"], phone=row["phone"], address=row["address"])


@router.post("", response_model=Customer, status_code=201)
def create_customer(payload: CustomerCreate):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO customers(name, phone, address) VALUES(?,?,?)",
        (payload.name, payload.phone, payload.address),
    )
    cid = cur.lastrowid
    conn.commit()
    conn.close()
    return get_customer(cid)


@router.put("/{customer_id}", response_model=Customer)
def update_customer(customer_id: int, payload: CustomerUpdate):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM customers WHERE id=?", (customer_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    name = payload.name if payload.name is not None else row["name"]
    phone = payload.phone if payload.phone is not None else row["phone"]
    address = payload.address if payload.address is not None else row["address"]

    cur.execute(
        "UPDATE customers SET name=?, phone=?, address=? WHERE id=?",
        (name, phone, address, customer_id),
    )
    conn.commit()
    conn.close()
    return get_customer(customer_id)


@router.delete("/{customer_id}", status_code=204)
def delete_customer(customer_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM customers WHERE id=?", (customer_id,))
    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    conn.commit()
    conn.close()
    return None