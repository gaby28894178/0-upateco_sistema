from fastapi import APIRouter, HTTPException
from ..db import get_connection, hash_password, create_token


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(username: str, password: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, password_hash, role FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    if not row or row["password_hash"] != hash_password(password):
        conn.close()
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    token = create_token(row["id"], 1)
    conn.close()
    return {"token": token, "username": username, "role": row["role"]}