from datetime import datetime, timezone
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship, create_engine, Session

# ─── Configuración de la Base de Datos ──────────────────────────────────────────
# Definimos el nombre del archivo y la URL de conexión para SQLite.
sqlite_file_name = "bistromaster.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# El motor (engine) maneja la comunicación con la base de datos.
# 'check_same_thread=False' es necesario para que SQLite funcione con FastAPI.
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

# ─── Modelos de Datos (Tablas) ──────────────────────────────────────────────────

class User(SQLModel, table=True):
    """
    Representa a los usuarios del sistema (Administradores y Personal).
    Se utiliza para la autenticación y control de acceso.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    role: str = Field(default="staff") # roles posibles: admin, staff

class MenuItem(SQLModel, table=True):
    """
    Representa un plato o bebida en el menú digital.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    price: float = Field(gt=0)
    category: str = Field(max_length=50) # Ejemplo: Entrada, Fuerte, Postre, Bebida
    image_url: Optional[str] = None

class OrderItem(SQLModel, table=True):
    """
    Tabla intermedia para los items de un pedido. 
    Relaciona un pedido específico con los productos del menú.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    menu_item_id: int = Field(foreign_key="menuitem.id")
    quantity: int = Field(ge=1)
    
    # Relaciones para facilitar el acceso a los datos desde el código.
    order: "Order" = Relationship(back_populates="items")

class Order(SQLModel, table=True):
    """
    Representa un pedido realizado por un cliente.
    Mantiene el estado y el total a pagar.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_name: str = Field(max_length=100)
    total_price: float = Field(default=0.0)
    # Estados: pendiente, en_preparacion, listo, entregado, cancelado
    status: str = Field(default="pendiente") 
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Una orden puede tener múltiples items.
    items: List[OrderItem] = Relationship(back_populates="order")

# ─── Inicialización y Utilidades ───────────────────────────────────────────────

def create_db_and_tables():
    """
    Crea la base de datos y todas las tablas definidas en los modelos.
    """
    SQLModel.metadata.create_all(engine)

def get_session():
    """
    Generador de sesiones para ser usado como dependencia en FastAPI.
    Asegura que la sesión se cierre correctamente después de cada petición.
    """
    with Session(engine) as session:
        yield session
