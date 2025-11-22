# Sistema de Gestión de Pedidos "El Tata" — SRS (IEEE 830)

## Resumen
- API REST funcionando para gestión de pedidos, productos y clientes.
- Basado en los requisitos del SRS según IEEE 830, con mejoras propuestas.
- Documentación, rutas para Postman, y diagramas de flujo y casos de uso.

## Endpoints y Exploración
- Base: `http://localhost:8000`
- Documentación interactiva: `http://localhost:8000/docs`
- Colección Postman: `postman/ElTata.postman_collection.json`

## Requisitos Funcionales (RF)
- RF-01 Registro de pedidos (cliente, productos, cantidades, observaciones, fecha/hora)
- RF-02 Gestión de estados del pedido (Pendiente → En preparación → Listo → Entregado/Cancelado)
- RF-03 Modificación de pedidos (solo en Pendiente/En preparación)
- RF-04 Gestión de productos (CRUD completo)
- RF-05 Cálculo automático (subtotal, impuestos, descuentos, total)
- RF-06 Gestión de clientes (registro y consulta)
- RF-07 Reportes de ventas (por período, top productos, ingresos, promedio ticket)
- RF-08 Notificaciones (pendiente de implementación)

## Requisitos No Funcionales (RNF)
- Usabilidad: interfaz de API con Swagger; futuras UI responsive.
- Rendimiento: respuesta típica < 3s en operaciones comunes.
- Seguridad: pendiente autenticación; HTTPS recomendado en despliegue.
- Disponibilidad: objetivo ≥98%; backups diarios recomendados.
- Escalabilidad: crecimiento a cientos de productos y pedidos diarios.
- Compatibilidad: navegadores modernos; API estándar HTTP/JSON.
- Backup: recomendación de backup automático diario.

## Interfaces del Sistema
- Usuario: roles Admin/Empleado (autenticación futura); paneles y formularios.
- Hardware: tablets y PCs; impresora de tickets.
- Comunicación: API REST; protocolo HTTPS recomendado.

## Modelo de Datos (simplificado)
- `customers(id, name, phone, address)`
- `products(id, name, description, price, category, available)`
- `orders(id, customer_id, status, created_at, notes)`
- `order_items(id, order_id, product_id, quantity, unit_price)`

## Casos de Uso (Mermaid)
```mermaid
flowchart TD
    U[Usuario] -->|Inicia sesión| A[Panel]
    A -->|Nuevo Pedido| NP[Registrar Pedido]
    NP -->|Agregar items| I[Selecciona Productos]
    NP -->|Confirmar| C[Crear Pedido]
    A -->|Gestionar| GE[Actualizar Estado]
    GE -->|Pendiente → En preparación → Listo → Entregado| FL[Flujo de Estados]
    A -->|Menú| MP[CRUD Productos]
    A -->|Clientes| CL[CRUD Clientes]
    A -->|Reportes| R[Reportes Ventas]
```

## Imágenes Modernas
- Casos de uso (SVG): ![Casos de uso](images/casos_uso.svg)
- Flujo de estados (SVG): ![Flujo de estados](images/flujo_estados.svg)

## Diagrama de Flujo de Estados
```mermaid
stateDiagram-v2
    [*] --> Pendiente
    Pendiente --> En_preparacion
    Pendiente --> Cancelado
    En_preparacion --> Listo
    En_preparacion --> Cancelado
    Listo --> Entregado
    Cancelado --> [*]
    Entregado --> [*]
```

## API (Resumen de Rutas)
- `GET /health`
- `GET /productos` | `GET /productos/{id}` | `POST /productos` | `PUT /productos/{id}` | `DELETE /productos/{id}`
- `GET /clientes` | `GET /clientes/{id}` | `POST /clientes` | `PUT /clientes/{id}` | `DELETE /clientes/{id}`
- `GET /pedidos?status=` | `GET /pedidos/{id}` (detalle con totales) | `POST /pedidos` (items) | `PUT /pedidos/{id}` (notas) | `POST /pedidos/{id}/estado` | `DELETE /pedidos/{id}`
- `GET /reportes/ventas?desde=&hasta=`
- `POST /auth/login` (autenticación básica; usuario seed `admin`/`admin`)
- `POST /auth/register` (alta de usuario)
- `POST /auth/logout` (cierre de sesión)
- `GET /auth/me` (validación del token y rol)
- `GET /pedidos/{id}/ticket` (ticket imprimible)

## Formatos de Datos
- Fechas: ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ`)
- Moneda: decimal (`price`, `unit_price`) en ARS.
- Estado: uno de `[Pendiente, En preparación, Listo, Entregado, Cancelado]`.

## Criterios de Aceptación
- Procesar 50 pedidos/hora sin degradación notable.
- Operaciones comunes < 3s de respuesta.
- Reportes generados en < 60s.
- Backup/restore de BD en < 30 min.

## Métricas de Calidad
- Cobertura de pruebas objetivo > 80% (pendiente de tests).
- Tiempo promedio de respuesta objetivo < 2s.
- Satisfacción de usuario > 4/5.

## Diagramas de Interfaz (Wireframes)

### Login
```
┌─────────────────────────────────────┐
│           EL TATA - LOGIN           │
├─────────────────────────────────────┤
│  Usuario: [ admin ]                 │
│  Contraseña: [  ••••••••• ]         │
│  [ ] Recordar usuario               │
│  [ INGRESAR ]                       │
└─────────────────────────────────────┘
```

### Dashboard
```
┌─────────────────────────────────────────────────────┐
│ EL TATA › Dashboard       [👤 Admin] [⚙] [🚪]       │
├─────────────────────────────────────────────────────┤
│  KPIs, pedidos recientes, accesos rápidos           │
│  [ NUEVO PEDIDO ]  [ MENÚ ]  [ REPORTES ]           │
└─────────────────────────────────────────────────────┘
```

### Nuevo Pedido
```
┌─────────────────────────────────────────────────────┐
│ CLIENTE, TELÉFONO, PRODUCTOS, ÍTEMS, TOTALES        │
│ [➕ Agregar] [ Cantidad ] [ CONFIRMAR PEDIDO ]       │
└─────────────────────────────────────────────────────┘
```

### Gestión de Estados
```
Pendientes | En preparación | Listos (Arrastrar/Acciones)  
[ ACTUALIZAR ]   [ NUEVO PEDIDO ]
```

### Gestión de Menú
```
Listado con filtros, edición y disponibilidad ✅/❌
```

### Reportes
```
Período, KPIs, top productos, gráficos, exportación PDF
```

## Despliegue y Configuración
- Base de datos: `ELTATA_DB_PATH` opcional para definir ruta del `.db`.
- Desarrollo: ejecutar servidor en `uvicorn app.main:app --reload`.
- CORS: habilitado para `*` en desarrollo; ajustar en producción.

## Autenticación
- Endpoint: `POST /auth/login` con `username` y `password`.
- Respuesta: `token`, `username`, `role`.
- Seed: usuario `admin` contraseña `admin`.
- Uso en frontend: guarda token y muestra badge de usuario.
- Registro: `POST /auth/register` devuelve token y rol inicial.
- Logout: `POST /auth/logout` invalida el token actual.
- Validación: `GET /auth/me` mantiene sesión y controla navegación.

## Reportes diarios
- Pestaña “Reportes” en frontend.
- KPIs: Total de ventas, pedidos, promedio ticket.
- Filtro por fecha “Desde/Hasta” o botón “Hoy”.

## Glosario
- Pedido: solicitud de productos de un cliente.
- Ítem de pedido: producto y cantidad asociada a un pedido.
- Estado: fase del ciclo de vida del pedido.
- Cliente: persona que realiza el pedido.
- Producto: bien ofrecido (pizza, bebida, etc.).

## Recomendaciones Futuras
- Autenticación y roles.
- Notificaciones (SMS/email) en cambio de estado.
- Exportación de reportes a PDF.
- UI admin y POS (tablet) con los wireframes anteriores.
## ESPECIFICACIÓN DE REQUISITOS DEL SOFTWARE (SRS) — SISTEMA "EL TATA"

### 1. Propósito
- Documentar de forma clara y verificable los requisitos del sistema "El Tata" para la gestión de pedidos, abarcando funcionalidades, datos, interfaces, flujos y criterios de validación.

### 2. Alcance
- Gestión integral de pedidos de un local gastronómico: menú, clientes, pedidos, repartidores, reportes y notificaciones.
- Usuario objetivo: administradores y empleados del local; consulta de estado por clientes.

### 3. Definiciones y Acrónimos
- Pedido: conjunto de ítems seleccionados por el cliente con total calculado.
- Ítem: producto del menú con cantidad y precio unitario.
- RF/RNF: Requisitos Funcionales / No Funcionales.
- KPI: indicador clave de desempeño (tiempo de registro, disponibilidad, errores).

### 4. Referencias
- API Docs: `http://127.0.0.1:8000/docs`
- Frontend: `http://127.0.0.1:8000/web`
- Repositorio: `https://github.com/gaby28894178/0-upateco_sistema`

### 5. Visión General del Producto
- El sistema centraliza el registro y gestión de pedidos, con cálculo automático, control de estado y métricas de ventas. Ofrece una UI tipo POS con tabs, login y roles.

### 6. Actores y Características
- Administrador: gestiona menú, usuarios y reportes.
- Empleado: registra y modifica pedidos, cancela antes del envío.
- Cliente: consulta estado y recibe notificaciones.

### Diagramas de Casos de Uso

Diagrama General (visual)

```
┌─────────────────────────────────────────────────────────────┐
│                    SISTEMA GESTIÓN PEDIDOS                  │
└─────────────────────────────────────────────────────────────┘
            ▲                          ▲                  ▲
            │                          │                  │
    ┌───────┼──────────────────────────┼──────────────────┼───────┐
    │       │                          │                  │       │
    ▼       ▼                          ▼                  ▼       ▼

[Administrador]                 [Empleado]              [Cliente]
    👨‍💼                         👨‍🍳                     👤
    │                            │                        │
    ├─ Gestionar Menú            ├─ Registrar Pedido      ├─ Recibir Notificación
    ├─ Generar Reportes          ├─ Modificar Pedido      └─ Consultar Estado
    └─ Administrar Usuarios      └─ Cancelar Pedido
```

Actores y Casos de Uso (detallado)

```
┌─────────────────────────────────────────┐
│             ADMINISTRADOR               │
├─────────────────────────────────────────┤
│ • Gestionar Menú Principal              │
│ • Generar Reportes de Ventas            │
│ • Administrar Usuarios del Sistema      │
│ • Configurar Parámetros del Sistema     │
└─────────────────────────────────────────┘

📝 GESTIONAR MENÚ
├── Agregar nuevo producto
├── Modificar producto existente
├── Eliminar producto
├── Actualizar precios
└── Categorizar productos

┌─────────────────────────────────────────┐
│               EMPLEADO                  │
├─────────────────────────────────────────┤
│ • Registrar Nuevos Pedidos              │
│ • Modificar Pedidos Existentes          │
│ • Cancelar Pedidos                      │
│ • Consultar Estado de Pedidos           │
│ • Calcular Totales Automáticos          │
└─────────────────────────────────────────┘

📋 REGISTRAR PEDIDO
├── Ingresar datos del cliente
├── Seleccionar productos del menú
├── Agregar observaciones especiales
├── Aplicar descuentos (si corresponde)
├── Calcular total automáticamente
└── Confirmar pedido

┌─────────────────────────────────────────┐
│                CLIENTE                  │
├─────────────────────────────────────────┤
│ • Recibir Notificaciones                │
│ • Consultar Estado del Pedido           │
│ • Realizar Consultas                    │
└─────────────────────────────────────────┘
```

### Requisitos Funcionales (visual)

Alta prioridad

```
🟥 RF-01: REGISTRO DE PEDIDOS
   └── 📝 Datos: Cliente + Productos + Observaciones

🟥 RF-02: MODIFICACIÓN/CANCELACIÓN
   └── ⚡ Antes del envío

🟥 RF-04: CÁLCULO AUTOMÁTICO
   └── 🧮 Total = Precios + Descuentos
```

Media prioridad

```
🟨 RF-03: GESTIÓN DE MENÚ
   └── ➕ Agregar / ✏️ Modificar / ❌ Eliminar

🟨 RF-05: REPORTES DE VENTAS
   └── 📊 Diarios • Semanales • Mensuales
```

Baja prioridad

```
🟩 RF-06: NOTIFICACIONES CLIENTE
   └── 🔔 Pedido listo • 📦 En camino
```

Listado detallado

- RF-01 Registro de pedidos: cliente, productos, observaciones, totales.
- RF-02 Modificación/Cancelación: permitido antes del estado "Enviado/Entregado".
- RF-03 Gestión de menú: alta, baja, modificación, categorías y disponibilidad.
- RF-04 Cálculo automático: subtotal, descuentos, total por ítems.
- RF-05 Reportes de ventas: por fecha, KPIs de total, cantidad y promedio.
- RF-06 Notificaciones al cliente: pedido listo, en camino.

### Requisitos No Funcionales (visual)

Alta prioridad

```
🟥 RNF-01: USABILIDAD
   └── 🎯 Interfaz intuitiva y fácil de usar

🟥 RNF-02: RENDIMIENTO
   └── ⏱️ Registro pedido < 5 segundos

🟥 RNF-03: SEGURIDAD
   └── 🔒 Datos almacenados cifrados
```

Media prioridad

```
🟨 RNF-04: DISPONIBILIDAD
   └── 📈 95% del tiempo operativo

🟨 RNF-05: ESCALABILIDAD
   └── 📊 Hasta 100 pedidos diarios
```

Baja prioridad

```
🟩 RNF-06: COMPATIBILIDAD
   └── 🌐 Chrome • Firefox • Edge
```

Listado detallado

- RNF-01 Usabilidad: interfaz clara, navegación consistente y responsive.
- RNF-02 Rendimiento: registrar pedido < 5 segundos en condiciones normales.
- RNF-03 Seguridad: contraseñas hash; tokens con expiración.
- RNF-04 Disponibilidad: 95% operativo en horario comercial.
- RNF-05 Escalabilidad: hasta 100 pedidos diarios sin degradación significativa.
- RNF-06 Compatibilidad: Chrome/Firefox/Edge actuales.

### Flujo del Proceso de Pedidos

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐    ┌─────────────┐
│   CLIENTE   │───▶│   EMPLEADO   │───▶│  SISTEMA     │───▶│ADMINISTRADOR│
│             │    │              │    │              │    │             │
│ Realiza     │    │ Registra     │    │ Calcula      │    │ Genera      │
│ pedido      │    │ pedido       │    │ total        │    │ reportes    │
└─────────────┘    └──────────────┘    └──────────────┘    └─────────────┘
                         │                    │                    │
                         ▼                    ▼                    ▼
                 ┌──────────────┐    ┌──────────────┐    ┌─────────────┐
                 │ Notificación │◀───│ Procesamiento│───▶│ Gestión     │
                 │ al cliente   │    │ del pedido   │    │ del menú    │
                 └──────────────┘    └──────────────┘    └─────────────┘
```

Narrativa

- El cliente realiza el pedido; el empleado registra ítems y observaciones.
- El sistema calcula totales y persiste el pedido; se asigna repartidor si aplica.
- El administrador consulta reportes y ajusta el menú según métricas.

### Criterios de Validación

```
✅ VALIDACIÓN POR PRIORIDAD
├── 🔴 ALTA: Pruebas unitarias + Pruebas de integración
├── 🟡 MEDIA: Pruebas de aceptación + Prototipos
└── 🟢 BAJA: Revisión con el cliente + Casos de prueba
```

Aceptación

- Alta prioridad: pruebas unitarias e integración deben pasar con >90% cobertura en módulos críticos.
- Media prioridad: pruebas de aceptación con escenarios de usuario y prototipos validados.
- Baja prioridad: revisión con el cliente y casos de prueba manuales documentados.

### Resumen Ejecutivo Visual

```
SISTEMA "EL TATA" - GESTIÓN DE PEDIDOS
├── 👥 3 ACTORES PRINCIPALES
├── 📋 6 REQUISITOS FUNCIONALES
├── 🛡️ 6 REQUISITOS NO FUNCIONALES
├── 🎯 3 NIVELES DE PRIORIDAD
└── 🔄 1 PROCESO UNIFICADO
```

Indicadores

- Tiempo de registro: objetivo < 5s.
- Tasa de errores: < 1% en operaciones diarias.
- Disponibilidad: ≥ 95% en horario de atención.

### Diagramas en código dbdiagram (para pegar fácilmente)

Casos de uso modelados (representación conceptual)

```
Table administrador {
  id int [pk]
  nombre varchar
  email varchar
  fecha_creacion timestamp
}

Table empleado {
  id int [pk]
  nombre varchar
  rol varchar
  activo boolean
}

Table cliente {
  id int [pk]
  nombre varchar
  telefono varchar
  email varchar
}

Table casos_uso {
  id int [pk]
  actor varchar
  caso_uso varchar
  descripcion text
}

Table gestion_menu {
  id int [pk]
  administrador_id int
  accion varchar
  fecha timestamp
}

Table pedido_cu {
  id int [pk]
  empleado_id int
  cliente_id int
  accion varchar
  fecha timestamp
}

Table notificacion {
  id int [pk]
  cliente_id int
  tipo varchar
  mensaje text
  fecha timestamp
}

Table reporte_ventas {
  id int [pk]
  administrador_id int
  tipo varchar
  periodo varchar
  total decimal
  fecha timestamp
}

Ref: gestion_menu.administrador_id > administrador.id
Ref: pedido_cu.empleado_id > empleado.id
Ref: pedido_cu.cliente_id > cliente.id
Ref: notificacion.cliente_id > cliente.id
Ref: reporte_ventas.administrador_id > administrador.id
```

Modelo de datos real del sistema

```
Table productos {
  id int [pk]
  name varchar
  price decimal
  category varchar
  available boolean
}

Table clientes {
  id int [pk]
  name varchar
  phone varchar
  address varchar
}

Table repartidores {
  id int [pk]
  name varchar
  phone varchar
}

Table pedidos {
  id int [pk]
  customer_id int
  driver_id int
  status varchar
  notes text
  total decimal
  created_at timestamp
}

Table order_items {
  id int [pk]
  order_id int
  product_id int
  quantity int
  unit_price decimal
}

Table users {
  id int [pk]
  username varchar [unique]
  password_hash varchar
  role varchar
}

Table auth_tokens {
  token varchar [pk]
  user_id int
  expires_at timestamp
}

Ref: pedidos.customer_id > clientes.id
Ref: pedidos.driver_id > repartidores.id
Ref: order_items.order_id > pedidos.id
Ref: order_items.product_id > productos.id
Ref: auth_tokens.user_id > users.id
```

### 7. Diccionario de Datos
- `productos`: catálogo del menú.
  - `id` (int), `name` (varchar), `price` (decimal), `category` (varchar), `available` (bool).
- `clientes`: datos del cliente.
  - `id` (int), `name` (varchar), `phone` (varchar), `address` (varchar).
- `repartidores`: asignación logística.
  - `id` (int), `name` (varchar), `phone` (varchar).
- `pedidos`: entidad principal.
  - `id` (int), `customer_id` (FK), `driver_id` (FK), `status` (varchar), `notes` (text), `total` (decimal), `created_at` (timestamp).
- `order_items`: ítems del pedido.
  - `id` (int), `order_id` (FK), `product_id` (FK), `quantity` (int), `unit_price` (decimal).
- `users`: autenticación.
  - `id` (int), `username` (varchar, único), `password_hash` (varchar), `role` (varchar).
- `auth_tokens`: sesión.
  - `token` (pk), `user_id` (FK), `expires_at` (timestamp).

### 8. Estados del Pedido
- `pendiente` → `preparando` → `listo` → `en_camino` → `entregado`.
- Cancelación permitida en `pendiente` y `preparando`.

### 9. API (Resumen y Ejemplos)
- `POST /auth/login`
  - Request: `{ "username": "caja1", "password": "***" }`
  - Response: `{ "token": "...", "user": { "id": 1, "role": "empleado" } }`
- `GET /productos`
  - Response: `[ { "id": 10, "name": "Empanada", "price": 700.0, "category": "comida", "available": true } ]`
- `POST /pedidos`
  - Request: `{ "customer_id": 3, "items": [ { "product_id": 10, "quantity": 6 } ], "notes": "sin sal" }`
  - Response: `{ "id": 120, "status": "pendiente", "total": 4200.0 }`
- `POST /pedidos/{id}/estado`
  - Request: `{ "status": "preparando" }`
  - Response: `{ "id": 120, "status": "preparando" }`
- `GET /reportes/ventas?desde=&hasta=`
  - Response: `{ "total": 152000.0, "count": 87, "avg": 1747.1 }`

### 10. Roles y Permisos
- Administrador: CRUD de menú y usuarios; reportes; configuración.
- Empleado: CRUD de pedidos (con restricciones de estado); consulta de productos/clientes.
- Cliente: consulta estado y notificaciones.

### 11. Suposiciones y Dependencias
- Persistencia SQLite; backend FastAPI; tokens Bearer; frontend POS con tabs.
- Compatibilidad con navegadores modernos.

### 12. Riesgos y Mitigaciones
- Pico de carga: colas de trabajo y cache; límites de concurrencia.
- Seguridad de datos: hash de contraseñas, expiración de tokens, evitar logs sensibles.
- UX en móviles: layout responsive, navbar compacto.

### 13. Trazabilidad (RF → Datos/Endpoints)
- RF-01 → `pedidos`, `order_items` • `/pedidos`.
- RF-02 → `pedidos.status` • `/pedidos/{id}/estado`, `DELETE /pedidos/{id}`.
- RF-03 → `productos` • `/productos` CRUD.
- RF-04 → `order_items.unit_price`, `pedidos.total` • lógica de cálculo.
- RF-05 → `reporte_ventas` • `/reportes/ventas`.
- RF-06 → `notificacion` • evento de estado.

### 14. Interfaz y Navegación
- Navbar junto al título en el header, con estado activo por pestaña y estilo compacto.
- Redirección automática a “Login” si no hay sesión.
- Login en card centrado; footer minimal para maximizar espacio útil.
- Vistas con tarjetas y scroll interno para acomodar contenido en el viewport.

### API (Resumen)
- `GET /health` estado del backend.
- `GET /productos`, `POST /productos`, `PUT /productos/{id}`, `DELETE /productos/{id}`.
- `GET /clientes`, `POST /clientes`, `PUT /clientes/{id}`, `DELETE /clientes/{id}`.
- `GET /repartidores`.
- `GET /pedidos`, `POST /pedidos`, `GET /pedidos/{id}`, `POST /pedidos/{id}/estado`, `DELETE /pedidos/{id}`.
- `GET /reportes/ventas?desde=&hasta=`.
- `POST /auth/login`, `POST /auth/register`, `POST /auth/logout`, `GET /auth/me`.
- `GET /pedidos/{id}/ticket`.

### Roles y Permisos
- Administrador: gestionar menú, usuarios y reportes.
- Empleado: registrar, modificar y cancelar pedidos.
- Cliente: consultar estado y recibir notificaciones.

### Suposiciones y Dependencias
- Persistencia SQLite; despliegue en FastAPI.
- Autenticación por token tipo Bearer.
- Frontend POS con tabs y login obligatorio.

### Riesgos y Mitigaciones
- Riesgo: saturación en horario pico → Mitigación: limitar llamadas concurrentes y cache de listas.
- Riesgo: datos sensibles → Mitigación: hash de contraseñas y expiración de tokens.
- Riesgo: UX en móviles → Mitigación: layout responsive y navbar compacto.

### Interfaz y Navegación
- Navbar junto al título en el header, con estado activo por pestaña y estilo compacto.
- Redirección automática a “Login” si no hay sesión.
- Login en card centrado con ancho estándar; footer minimal para maximizar espacio útil.
- Vistas con tarjetas y scroll interno para acomodar contenido en el viewport.
Listado detallado

- RF-01 Registro de pedidos: cliente, productos, observaciones, totales.
- RF-02 Modificación/Cancelación: permitido antes del estado "Enviado/Entregado".
- RF-03 Gestión de menú: alta, baja, modificación, categorías y disponibilidad.
- RF-04 Cálculo automático: subtotal, descuentos, total por ítems.
- RF-05 Reportes de ventas: por fecha, KPIs de total, cantidad y promedio.
- RF-06 Notificaciones al cliente: pedido listo, en camino.
Listado detallado

- RNF-01 Usabilidad: interfaz clara, navegación consistente y responsive.
- RNF-02 Rendimiento: registrar pedido < 5 segundos en condiciones normales.
- RNF-03 Seguridad: contraseñas hash; tokens con expiración.
- RNF-04 Disponibilidad: 95% operativo en horario comercial.
- RNF-05 Escalabilidad: hasta 100 pedidos diarios sin degradación significativa.
- RNF-06 Compatibilidad: Chrome/Firefox/Edge actuales.
Narrativa

- El cliente realiza el pedido; el empleado registra ítems y observaciones.
- El sistema calcula totales y persiste el pedido; se asigna repartidor si aplica.
- El administrador consulta reportes y ajusta el menú según métricas.
Aceptación

- Alta prioridad: pruebas unitarias e integración deben pasar con >90% cobertura en módulos críticos.
- Media prioridad: pruebas de aceptación con escenarios de usuario y prototipos validados.
- Baja prioridad: revisión con el cliente y casos de prueba manuales documentados.
Indicadores

- Tiempo de registro: objetivo < 5s.
- Tasa de errores: < 1% en operaciones diarias.
- Disponibilidad: ≥ 95% en horario de atención.