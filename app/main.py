from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routers.health import router as health_router
from .routers.products import router as products_router
from .routers.customers import router as customers_router
from .routers.orders import router as orders_router
from .routers.reports import router as reports_router
from .routers.drivers import router as drivers_router
from .routers.docs import router as docs_router
from .routers.auth import router as auth_router
from .db import init_db


def create_app() -> FastAPI:
    app = FastAPI(
        title="El Tata - Sistema de Gestión de Pedidos",
        version="0.1.0",
        description="API REST para gestión de pedidos, productos y clientes",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(products_router)
    app.include_router(customers_router)
    app.include_router(orders_router)
    app.include_router(reports_router)
    app.include_router(drivers_router)
    app.include_router(docs_router)
    app.include_router(auth_router)

    app.mount("/web", StaticFiles(directory="frontend", html=True), name="web")

    return app


app = create_app()


@app.on_event("startup")
def on_startup():
    init_db()
    from .db import seed_admin
    seed_admin()