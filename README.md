# BistroMaster PRO - Pedidos de restaurante

**BistroMaster PRO** es una solución integral y profesional para la gestión de restaurantes, diseñada para ofrecer una experiencia perfecta tanto para el cliente como para el personal administrativo.

Este proyecto ha sido desarrollado como una **API de extremo a extremo** con un frontend moderno y elegante.

## Características Principales

- **API REST Robusta**: Desarrollada con FastAPI y SQLModel.
- **Base de Datos Persistente**: Implementación con SQLite para facilitar la portabilidad.
- **Seguridad JWT**: Acceso administrativo protegido mediante JSON Web Tokens.
- **Frontend Premium**: Interfaz de usuario diseñada con técnicas modernas de CSS (Glassmorphism, Responsive).
- **Dashboard Administrativo**: Monitoreo de pedidos en tiempo real y gestión dinámica del menú.
- **Reporte Automático**: Generador de documentación en formato Word para entrega académica.

## Tecnologías

| Componente | Tecnología |
| :--- | :--- |
| **Backend** | Python 3.12, FastAPI, SQLModel |
| **Database** | SQLite (Relacional) |
| **Seguridad** | OAuth2, JWT, Bcrypt |
| **Frontend** | Vanilla JavaScript, HTML5, CSS3 Moderno |
| **Manuals** | python-docx |

## Instalación y Uso

### 1. Preparar el entorno
```bash
# Crear venv (si no existe)
python -m venv venv
# Activar venv
source venv/bin/activate  # Linux/Mac
# Instalar dependencias
pip install -r requirements.txt
```

### 2. Inicializar Datos
```bash
# Sembrar la base de datos con platos de ejemplo y usuario admin
python seed.py
```

### 3. Ejecutar el Servidor
```bash
python -m uvicorn main:app --reload
```
La API estará disponible en `http://localhost:8000`.
La documentación interactiva (Swagger) en `http://localhost:8000/docs`.

### 4. Acceder al Frontend
- **Menú Cliente**: Abre `frontend/index.html` en tu navegador.
- **Panel Staff**: Abre `frontend/admin.html` (Credenciales: `admin` / `admin123`).
---
*Desarrollado por Humberto Alejandro Zambrano - Programación III B*
