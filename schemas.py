from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# ─── Esquemas de Autenticación ────────────────────────────────────────────────
# Estos modelos definen la estructura de los datos para el manejo de tokens.

class Token(BaseModel):
    """Estructura básica del token de acceso devuelto al iniciar sesión."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Datos contenidos dentro del payload del JWT (normalmente el nombre de usuario)."""
    username: Optional[str] = None

# ─── Esquemas del Menú ─────────────────────────────────────────────────────────

class MenuItemBase(BaseModel):
    """Campos base que comparten la creación y lectura de items del menú."""
    name: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    price: float = Field(..., gt=0)
    category: str = Field(..., max_length=50)
    image_url: Optional[str] = None

class MenuItemCreate(MenuItemBase):
    """Esquema utilizado para recibir los datos de un nuevo item desde el frontend."""
    pass

class MenuItemRead(MenuItemBase):
    """Esquema utilizado para enviar los datos de un item hacia el frontend (incluye ID)."""
    id: int

# ─── Esquemas de Pedidos (Orders) ──────────────────────────────────────────────

class OrderItemCreate(BaseModel):
    """Datos necesarios para añadir un item a una orden."""
    menu_item_id: int
    quantity: int = Field(..., ge=1)

class OrderItemRead(OrderItemCreate):
    """Datos de un item de orden al consultarlos (incluye ID único del registro)."""
    id: int

class OrderCreate(BaseModel):
    """Esquema completo para crear una nueva orden con varios items."""
    customer_name: str = Field(..., max_length=100)
    items: List[OrderItemCreate]

class OrderRead(BaseModel):
    """Detalle completo de una orden para ser mostrado al administrador o personal."""
    id: int
    customer_name: str
    total_price: float
    status: str
    created_at: datetime
    items: List[OrderItemRead]

class OrderUpdateStatus(BaseModel):
    """Esquema para actualizar el estado de una orden, validando que sea uno de los permitidos."""
    # Los estados permitidos son: pendiente, en_preparacion, listo, entregado, cancelado
    status: str = Field(..., pattern="^(pendiente|en_preparacion|listo|entregado|cancelado)$")
