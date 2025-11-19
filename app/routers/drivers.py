from typing import List
from fastapi import APIRouter, HTTPException
from ..db import get_connection
from ..schemas import Driver, DriverCreate, DriverUpdate


router = APIRouter(prefix="/repartidores", tags=["repartidores"])


@router.get("", response_model=List[Driver])
def list_drivers():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, phone FROM drivers")
    rows = cur.fetchall()
    conn.close()
    return [Driver(id=r["id"], name=r["name"], phone=r["phone"]) for r in rows]


@router.get("/{driver_id}", response_model=Driver)
def get_driver(driver_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, phone FROM drivers WHERE id=?", (driver_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Repartidor no encontrado")
    return Driver(id=row["id"], name=row["name"], phone=row["phone"])


@router.post("", response_model=Driver, status_code=201)
def create_driver(payload: DriverCreate):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO drivers(name, phone) VALUES(?,?)", (payload.name, payload.phone))
    did = cur.lastrowid
    conn.commit()
    conn.close()
    return get_driver(did)


@router.put("/{driver_id}", response_model=Driver)
def update_driver(driver_id: int, payload: DriverUpdate):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM drivers WHERE id=?", (driver_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Repartidor no encontrado")
    name = payload.name if payload.name is not None else row["name"]
    phone = payload.phone if payload.phone is not None else row["phone"]
    cur.execute("UPDATE drivers SET name=?, phone=? WHERE id=?", (name, phone, driver_id))
    conn.commit()
    conn.close()
    return get_driver(driver_id)


@router.delete("/{driver_id}", status_code=204)
def delete_driver(driver_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM drivers WHERE id=?", (driver_id,))
    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Repartidor no encontrado")
    conn.commit()
    conn.close()
    return None