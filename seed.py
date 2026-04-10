from sqlmodel import Session, create_engine
from database import User, MenuItem, SQLModel
from auth import get_password_hash

# Configuración local para el proceso de carga de datos.
sqlite_url = "sqlite:///bistromaster.db"
engine = create_engine(sqlite_url)

def seed(force: bool = False):
    """
    Puebla la base de datos con datos iniciales necesarios para el funcionamiento.
    Crea un administrador predeterminado y platos típicos ecuatorianos.
    """
    # Nos aseguramos de que las tablas existan antes de insertar datos.
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        # 1. Creación del Usuario Administrador
        # Verificamos si ya existe para no duplicarlo.
        if not session.query(User).filter(User.username == "admin").first():
            admin = User(
                username="admin", 
                # Contraseña por defecto: admin123
                hashed_password=get_password_hash("admin123"),
                role="admin"
            )
            session.add(admin)
            print("🚀 Usuario 'admin' creado exitosamente.")
        
        # 2. Carga del Menú (Platos típicos de Ecuador)
        existing_count = session.query(MenuItem).count()
        if existing_count > 0 and not force:
            print(f"✅ El menú ya tiene {existing_count} platos. Saltando carga inicial.")
            return

        if force:
            print("⚠️ Forzando recarga: Limpiando platos existentes...")
            session.query(MenuItem).delete()
        
        # Listado de platos sugeridos para el proyecto.
        items = [
            {"name": "Ceviche de Camarón", "description": "Clásico ceviche ecuatoriano con camarones frescos, limón, naranja y cilantro.", "price": 10.50, "category": "Entrada", "image_url": "images/ceviche.jpg"},
            {"name": "Locro de Papa", "description": "Sopa cremosa de papas con queso, aguacate y granos de choclo.", "price": 5.50, "category": "Entrada", "image_url": "images/locro.jpg"},
            {"name": "Encebollado de Albacora", "description": "La joya de la costa: sopa de pescado con yuca, abundante cebolla curtida y chifles.", "price": 8.50, "category": "Fuerte", "image_url": "images/encebollado.jpg"},
            {"name": "Fritada Quiteña", "description": "Trozos de cerdo confitados acompañados de mote, maduro, aguacate y llapingachos.", "price": 12.00, "category": "Fuerte", "image_url": "images/fritada.jpg"},
            {"name": "Seco de Chivo", "description": "Guiso tradicional de chivo cocinado lentamente con cerveza y especias, servido con arroz amarillo.", "price": 14.50, "category": "Fuerte", "image_url": "images/seco_chivo.jpg"},
            {"name": "Helado de Paila", "description": "Helado artesanal batido en paila de bronce con frutas naturales.", "price": 4.00, "category": "Postre", "image_url": "images/helado_paila.jpg"},
            {"name": "Higos con Queso", "description": "Higos cocidos en miel de panela acompañados de queso fresco.", "price": 4.50, "category": "Postre", "image_url": "images/higos_queso.jpg"},
            {"name": "Jugo de Tomate de Árbol", "description": "Bebida refrescante de fruta exótica andina.", "price": 2.50, "category": "Bebida", "image_url": "images/jugo_tomate.jpg"},
            {"name": "Canelazo", "description": "Bebida caliente de agua de canela, panela y un toque de aguardiente.", "price": 3.50, "category": "Bebida", "image_url": "images/canelazo.jpg"}
        ]
        
        print(f"🍽️  Cargando {len(items)} delicias ecuatorianas al menú...")
        for item_data in items:
            item = MenuItem(**item_data)
            session.add(item)
        
        session.commit()
        print("✨ ¡Base de datos inicializada correctamente!")

if __name__ == "__main__":
    # Si ejecutamos este script directamente, forzamos la recarga.
    seed(force=True)
