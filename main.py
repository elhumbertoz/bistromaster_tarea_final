from datetime import timedelta
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select

# Importaciones Internas (Base de datos, Esquemas y Seguridad)
from database import create_db_and_tables, get_session, User, MenuItem, Order, OrderItem
from schemas import (
    Token, MenuItemCreate, MenuItemRead, 
    OrderCreate, OrderRead, OrderUpdateStatus
)
from auth import (
    verify_password, create_access_token, get_password_hash, 
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
)
from seed import seed

# ─── Configuración de la Aplicación ─────────────────────────────────────────────

app = FastAPI(
    title="BistroMaster PRO API",
    description="Sistema Profesional de Gestión de Restaurantes - Proyecto Universitario",
    version="2.0.0",
)

# Configuración de CORS para permitir que el Frontend se comunique con la API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción, especificar dominios exactos.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    """
    Se ejecuta al iniciar el servidor. 
    Crea las tablas y carga los datos iniciales (admin y menú) si no existen.
    """
    seed()

# ─── Endpoints de Autenticación ────────────────────────────────────────────────

@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    """
    Permite el inicio de sesión para administradores y personal.
    Devuelve un token JWT si las credenciales son válidas.
    """
    statement = select(User).where(User.username == form_data.username)
    user = session.exec(statement).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# ─── Endpoints del Menú ─────────────────────────────────────────────────────────

@app.get("/menu", response_model=List[MenuItem])
async def list_menu(session: Session = Depends(get_session)):
    """Obtiene la lista completa de platos y bebidas disponibles."""
    return session.exec(select(MenuItem)).all()

@app.get("/menu/{id}", response_model=MenuItem)
async def get_menu_item(id: int, session: Session = Depends(get_session)):
    """Obtiene el detalle de un item específico del menú por su ID."""
    item = session.get(MenuItem, id)
    if not item:
        raise HTTPException(status_code=404, detail="El plato o bebida solicitado no existe")
    return item

@app.post("/menu", response_model=MenuItem, status_code=201)
async def add_menu_item(
    item_data: MenuItemCreate, 
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Permite añadir un nuevo item al menú (Solo personal autorizado)."""
    item = MenuItem.model_validate(item_data)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

@app.delete("/menu/{id}", status_code=204)
async def delete_menu_item(
    id: int, 
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Elimina un item del menú por su ID (Solo personal autorizado)."""
    item = session.get(MenuItem, id)
    if not item:
        raise HTTPException(status_code=404, detail="El plato o bebida no fue encontrado")
    session.delete(item)
    session.commit()
    return None

# ─── Endpoints de Pedidos (Orders) ──────────────────────────────────────────────

@app.post("/orders", response_model=OrderRead, status_code=201)
async def create_order(order_data: OrderCreate, session: Session = Depends(get_session)):
    """
    Crea un nuevo pedido con múltiples items.
    Calcula el total automáticamente basándose en los precios del menú.
    """
    db_order = Order(customer_name=order_data.customer_name)
    session.add(db_order)
    session.commit()
    session.refresh(db_order)
    
    total = 0.0
    order_items = []
    for item in order_data.items:
        menu_item = session.get(MenuItem, item.menu_item_id)
        if not menu_item:
            # Si el item no existe, borramos la orden creada para mantener consistencia.
            session.delete(db_order)
            session.commit()
            raise HTTPException(status_code=404, detail=f"El producto con ID {item.menu_item_id} no existe")
        
        db_item = OrderItem(
            order_id=db_order.id,
            menu_item_id=item.menu_item_id,
            quantity=item.quantity
        )
        total += menu_item.price * item.quantity
        order_items.append(db_item)
        session.add(db_item)
    
    db_order.total_price = total
    session.add(db_order)
    session.commit()
    session.refresh(db_order)
    return db_order

@app.get("/orders", response_model=List[OrderRead])
async def list_orders(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Obtiene el listado de todos los pedidos realizados (Requiere autenticación)."""
    # Cargamos todas las órdenes. SQLModel maneja las relaciones automáticamente.
    return session.exec(select(Order)).all()

@app.get("/orders/{id}", response_model=OrderRead)
async def get_order(
    id: int, 
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Obtiene el detalle de un pedido específico por su ID."""
    order = session.get(Order, id)
    if not order:
        raise HTTPException(status_code=404, detail="El pedido solicitado no fue encontrado")
    return order

@app.patch("/orders/{id}/status", response_model=OrderRead)
async def update_order_status(
    id: int, 
    status_data: OrderUpdateStatus, 
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Actualiza el estado de un pedido (ej: de 'pendiente' a 'listo')."""
    order = session.get(Order, id)
    if not order:
        raise HTTPException(status_code=404, detail="No se encontró el pedido para actualizar")
    
    order.status = status_data.status
    session.add(order)
    session.commit()
    session.refresh(order)
    return order

# ─── Archivos Estáticos (Frontend) ───────────────────────────────────────────────
# Esta línea sirve el sitio web (HTML/JS/CSS) desde la carpeta 'frontend'.
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
