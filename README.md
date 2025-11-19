# 0-upateco_sistema

Sistema de Gestión de Pedidos "El Tata" — Backend FastAPI + Frontend POS simple.

- API: `http://127.0.0.1:8000` · Docs Swagger: `http://127.0.0.1:8000/docs`
- Frontend: `http://127.0.0.1:8000/web`
- SRS PDF: `http://127.0.0.1:8000/docs/srs.pdf`

Características:
- Productos, Clientes, Pedidos con estados y ticket imprimible
- Repartidores con asignación a pedido
- Reportes de ventas diarios (total, cantidad, promedio, top productos)
- Login simple (`admin/admin`) y token en frontend
- Registro y logout con mantenimiento de sesión (`/auth/register`, `/auth/logout`, `/auth/me`)
- Navegación junto al título en el header y redirección a Login sin sesión
 - Navbar semántico (`nav > ul > li > a`) con estilo compacto e iconos
 - Login centrado con ancho limitado y footer minimal

Instalación:
- `pip install fastapi uvicorn reportlab svglib`
- `python -m uvicorn app.main:app --reload --port 8000`

Colección Postman: `postman/ElTata.postman_collection.json`
 
 Autenticación:
 - `POST /auth/login` · `POST /auth/register` · `POST /auth/logout` · `GET /auth/me`
 - Frontend guarda token, muestra perfil y habilita “Logout”