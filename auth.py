from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select
from database import get_session, User
from schemas import TokenData

# ─── Configuración de Seguridad ───────────────────────────────────────────────
# LLAVE SECRETA: En un entorno de producción, esto debería estar en una variable de entorno.
SECRET_KEY = "RestauranteSecretoMuyPoderosoParaPedidosSeguros"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Configuración para el cifrado de contraseñas (Hashing).
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema de autenticación OAuth2 con el endpoint donde se solicita el token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ─── Lógica de Seguridad ───────────────────────────────────────────────────────

def verify_password(plain_password, hashed_password):
    """Verifica si una contraseña plana coincide con su versión cifrada."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Genera un hash seguro para la contraseña del usuario."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Crea un token JWT con una fecha de expiración.
    Útil para mantener sesiones seguras y temporales.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    session: Session = Depends(get_session)
):
    """
    Dependencia para obtener el usuario autenticado a partir del token JWT.
    Si el token es inválido o el usuario no existe, lanza una excepción 401.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales o la sesión ha expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decodificamos el token usando nuestra llave secreta.
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    # Buscamos al usuario en la base de datos por su nombre de usuario.
    statement = select(User).where(User.username == token_data.username)
    user = session.exec(statement).first()
    
    if user is None:
        raise credentials_exception
    return user
