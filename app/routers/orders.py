from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse
from ..db import get_connection, now_iso, ALLOWED_STATUSES
from ..schemas import OrderCreate, Order, OrderDetail


router = APIRouter(prefix="/pedidos", tags=["pedidos"])


def _order_to_model(row) -> Order:
    return Order(
        id=row["id"],
        customer_id=row["customer_id"],
        status=row["status"],
        created_at=row["created_at"],
        notes=row["notes"],
    )


@router.get("", response_model=List[Order])
def list_orders(status: Optional[str] = Query(default=None)):
    conn = get_connection()
    cur = conn.cursor()
    if status:
        cur.execute("SELECT * FROM orders WHERE status=? ORDER BY id DESC", (status,))
    else:
        cur.execute("SELECT * FROM orders ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return [_order_to_model(r) for r in rows]


@router.get("/{order_id}", response_model=OrderDetail)
def get_order(order_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE id=?", (order_id,))
    order_row = cur.fetchone()
    if not order_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    cur.execute(
        """
        SELECT oi.id, p.name as product, oi.quantity, oi.unit_price
        FROM order_items oi
        JOIN products p ON p.id = oi.product_id
        WHERE oi.order_id = ?
        """,
        (order_id,),
    )
    items = [dict(id=r["id"], product=r["product"], quantity=r["quantity"], unit_price=r["unit_price"]) for r in cur.fetchall()]

    subtotal = sum(i["quantity"] * i["unit_price"] for i in items)
    impuestos = 0.0
    descuentos = 0.0
    total = subtotal + impuestos - descuentos
    repartidor = None
    if order_row["driver_id"]:
        cur.execute("SELECT id, name, phone FROM drivers WHERE id=?", (order_row["driver_id"],))
        dr = cur.fetchone()
        if dr:
            repartidor = {"id": dr["id"], "name": dr["name"], "phone": dr["phone"]}
    conn.close()

    return OrderDetail(order=_order_to_model(order_row), items=items, subtotal=subtotal, impuestos=impuestos, descuentos=descuentos, total=total, repartidor=repartidor)


@router.post("", response_model=Order, status_code=201)
def create_order(payload: OrderCreate):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM customers WHERE id=?", (payload.customer_id,))
    if not cur.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Cliente inválido")

    created_at = now_iso()
    cur.execute(
        "INSERT INTO orders(customer_id, status, created_at, notes) VALUES(?,?,?,?)",
        (payload.customer_id, "Pendiente", created_at, payload.notes),
    )
    oid = cur.lastrowid

    if payload.driver_id is not None:
        cur.execute("SELECT id FROM drivers WHERE id=?", (payload.driver_id,))
        dr = cur.fetchone()
        if not dr:
            conn.rollback()
            conn.close()
            raise HTTPException(status_code=400, detail="Repartidor inválido")
        cur.execute("UPDATE orders SET driver_id=? WHERE id=?", (payload.driver_id, oid))

    for item in payload.items:
        cur.execute("SELECT price FROM products WHERE id=? AND available=1", (item.product_id,))
        row = cur.fetchone()
        if not row:
            conn.rollback()
            conn.close()
            raise HTTPException(status_code=400, detail=f"Producto {item.product_id} inválido o no disponible")
        unit_price = row["price"]
        cur.execute(
            "INSERT INTO order_items(order_id, product_id, quantity, unit_price) VALUES(?,?,?,?)",
            (oid, item.product_id, item.quantity, unit_price),
        )

    conn.commit()
    conn.close()
    return get_order(oid).order


@router.put("/{order_id}", response_model=Order)
def update_order(order_id: int, notes: Optional[str] = None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE id=?", (order_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    if row["status"] not in ("Pendiente", "En preparación"):
        conn.close()
        raise HTTPException(status_code=409, detail="Pedido no modificable en este estado")

    cur.execute("UPDATE orders SET notes=? WHERE id=?", (notes if notes is not None else row["notes"], order_id))
    conn.commit()
    conn.close()
    return get_order(order_id).order


@router.post("/{order_id}/estado", response_model=Order)
def change_status(order_id: int, nuevo_estado: str):
    if nuevo_estado not in ALLOWED_STATUSES:
        raise HTTPException(status_code=400, detail="Estado inválido")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE id=?", (order_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    actual = row["status"]
    transiciones_validas = {
        "Pendiente": {"En preparación", "Cancelado"},
        "En preparación": {"Listo", "Cancelado"},
        "Listo": {"Entregado"},
        "Entregado": set(),
        "Cancelado": set(),
    }

    if nuevo_estado not in transiciones_validas.get(actual, set()):
        conn.close()
        raise HTTPException(status_code=409, detail=f"Transición no permitida: {actual} → {nuevo_estado}")

    cur.execute("UPDATE orders SET status=? WHERE id=?", (nuevo_estado, order_id))
    conn.commit()
    conn.close()
    return get_order(order_id).order


@router.post("/{order_id}/asignar", response_model=Order)
def assign_driver(order_id: int, driver_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE id=?", (order_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    cur.execute("SELECT id FROM drivers WHERE id=?", (driver_id,))
    dr = cur.fetchone()
    if not dr:
        conn.close()
        raise HTTPException(status_code=404, detail="Repartidor no encontrado")
    cur.execute("UPDATE orders SET driver_id=? WHERE id=?", (driver_id, order_id))
    conn.commit()
    conn.close()
    return get_order(order_id).order


@router.delete("/{order_id}", status_code=204)
def delete_order(order_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT status FROM orders WHERE id=?", (order_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if row["status"] not in ("Pendiente", "Cancelado"):
        conn.close()
        raise HTTPException(status_code=409, detail="Pedido no puede eliminarse en este estado")

    cur.execute("DELETE FROM order_items WHERE order_id=?", (order_id,))
    cur.execute("DELETE FROM orders WHERE id=?", (order_id,))
    conn.commit()
    conn.close()
    return None


@router.get("/{order_id}/ticket", response_class=HTMLResponse)
def ticket(order_id: int):
    detail = get_order(order_id)
    o = detail.order
    items = detail.items
    subtotal = detail.subtotal
    total = detail.total
    impuestos = detail.impuestos
    descuentos = detail.descuentos
    cliente = o.customer_id
    repartidor = detail.repartidor
    html = f"""
    <!doctype html>
    <html lang=es>
    <head>
      <meta charset=utf-8>
      <title>Ticket #{o.id}</title>
      <style>
        body{{font-family:Segoe UI,Roboto,sans-serif;background:#fafafa;color:#111;}}
        .ticket{{width:360px;margin:16px auto;padding:16px;border:1px solid #ddd;border-radius:8px;background:#fff}}
        h1{{font-size:18px;margin:0 0 8px}}
        .row{{display:flex;justify-content:space-between;margin:4px 0}}
        .small{{color:#666;font-size:12px}}
        .items{{margin-top:8px;border-top:1px dashed #ccc}}
        .item{{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px dashed #eee}}
        .total{{font-weight:700}}
        .kpi{{display:flex;justify-content:space-between;margin-top:8px}}
        .print{{margin-top:12px}}
      </style>
    </head>
    <body>
      <div class=ticket>
        <h1>El Tata · Ticket #{o.id}</h1>
        <div class=row><span>Fecha</span><span class=small>{o.created_at}</span></div>
        <div class=row><span>Cliente ID</span><span>{cliente}</span></div>
        <div class=row><span>Repartidor</span><span>{(repartidor or {}).get('name','-')}</span></div>
        <div class=row><span>Estado</span><span>{o.status}</span></div>
        <div class=items>
          {''.join([f"<div class='item'><span>{i['product']}</span><span>{i['quantity']} × {i['unit_price']:.2f}</span></div>" for i in items])}
        </div>
        <div class=kpi><span>Subtotal</span><span>{subtotal:.2f}</span></div>
        <div class=kpi><span>Impuestos</span><span>{impuestos:.2f}</span></div>
        <div class=kpi><span>Descuentos</span><span>{descuentos:.2f}</span></div>
        <div class=kpi total><span>Total</span><span>{total:.2f}</span></div>
        <div class=print>
          <button onclick="window.print()">Imprimir</button>
        </div>
      </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html, status_code=200)