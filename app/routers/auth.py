from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from ..db import get_connection, hash_password, create_token, validate_token, revoke_token


router = APIRouter(prefix="/auth", tags=["auth"])


class LoginPayload(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(payload: LoginPayload):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, password_hash, role FROM users WHERE username=?", (payload.username,))
    row = cur.fetchone()
    if not row or row["password_hash"] != hash_password(payload.password):
        conn.close()
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    token = create_token(row["id"], 1)
    conn.close()
    return {"token": token, "username": payload.username, "role": row["role"]}


@router.get("/me")
def me(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="No autorizado")
    token = authorization.split(" ", 1)[1]
    user = validate_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Token inválido")
    return user


class RegisterPayload(BaseModel):
    username: str
    password: str
    role: str | None = "empleado"


@router.post("/register")
def register(payload: RegisterPayload):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username=?", (payload.username,))
    if cur.fetchone():
        conn.close()
        raise HTTPException(status_code=409, detail="Usuario ya existe")
    cur.execute(
        "INSERT INTO users(username, password_hash, role) VALUES(?,?,?)",
        (payload.username, hash_password(payload.password), payload.role or "empleado"),
    )
    uid = cur.lastrowid
    conn.commit()
    conn.close()
    token = create_token(uid, 1)
    return {"token": token, "username": payload.username, "role": payload.role or "empleado"}


@router.post("/logout")
def logout(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="No autorizado")
    token = authorization.split(" ", 1)[1]
    ok = revoke_token(token)
    if not ok:
        raise HTTPException(status_code=401, detail="Token inválido")
    return {"ok": True}