from typing import Optional, List, Dict
from fastapi import APIRouter, Query
from ..db import get_connection


router = APIRouter(prefix="/reportes", tags=["reportes"])


@router.get("/ventas")
def ventas(desde: Optional[str] = Query(default=None), hasta: Optional[str] = Query(default=None)):
    conn = get_connection()
    cur = conn.cursor()

    params = []
    where = []
    if desde:
        where.append("created_at >= ?")
        params.append(desde)
    if hasta:
        where.append("created_at <= ?")
        params.append(hasta)

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    cur.execute(
        f"""
        SELECT o.id
        FROM orders o
        {where_sql}
        """,
        params,
    )
    pedidos = [r["id"] for r in cur.fetchall()]

    total_ventas = 0.0
    for oid in pedidos:
        cur.execute("SELECT quantity, unit_price FROM order_items WHERE order_id=?", (oid,))
        total_ventas += sum(r["quantity"] * r["unit_price"] for r in cur.fetchall())

    cur.execute(
        f"""
        SELECT p.name, SUM(oi.quantity) as qty
        FROM order_items oi
        JOIN orders o ON o.id = oi.order_id
        JOIN products p ON p.id = oi.product_id
        {where_sql}
        GROUP BY p.name
        ORDER BY qty DESC
        LIMIT 5
        """,
        params,
    )
    top_productos = [{"producto": r["name"], "cantidad": r["qty"]} for r in cur.fetchall()]

    conn.close()
    return {
        "total_ventas": total_ventas,
        "pedidos": len(pedidos),
        "promedio_ticket": (total_ventas / len(pedidos)) if pedidos else 0.0,
        "top_productos": top_productos,
    }