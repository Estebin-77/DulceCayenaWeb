#  DulceCayenaWeb

**DulceCayenaWeb** es una aplicación web desarrollada con **Django y PostgreSQL** para una repostería artesanal.  
El sistema permite gestionar productos, servicios, pedidos, contacto y publicaciones de blog con un diseño moderno, minimalista y funcional.

---

##  Tecnologías utilizadas

- **Python 3.10+**
- **Django 5.2.7**
- **PostgreSQL**
- **HTML5, CSS3 y Bootstrap**
- **JavaScript (ES6)**
- **Git y GitHub**
- **python-dotenv** para la gestión segura de variables de entorno

---

## Instalación y ejecución local

Sigue estos pasos para ejecutar el proyecto en tu máquina local 👇

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/Estebin-77/DulceCayenaWeb.git
cd DulceCayenaWeb

2️⃣ Crear y activar el entorno virtual
python -m venv venv
venv\Scripts\activate   # En Windows
# source venv/bin/activate  # En Linux/Mac

3️⃣ Instalar dependencias
pip install -r requirements.txt

4️⃣ Configurar variables de entorno

Crea un archivo .env en la raíz del proyecto con tus datos:

SECRET_KEY=django-inseguro-cambia-esta-clave-por-una-real
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=dulcecayena
DB_USER=postgres
DB_PASSWORD=07041992
DB_HOST=localhost
DB_PORT=5432

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_correo@gmail.com
EMAIL_HOST_PASSWORD=tu_clave_de_aplicacion

Importante: nunca subas este archivo a GitHub, ya está protegido por .gitignore.

5️⃣ Aplicar migraciones

python manage.py migrate

6️⃣ Ejecutar el servidor

python manage.py runserver

Luego entra en tu navegador a http://127.0.0.1:8000/

Estructura del proyecto
DulceCayenaWeb/
│
├── manage.py
├── .env
├── .gitignore
├── README.md
├── requirements.txt
│
├── ProyectoDulceCayena/    # Configuración principal del proyecto
├── inicio/                 # Página de inicio y contenido estático
├── servicios/              # App de servicios de repostería
├── tienda/                 # App de tienda con productos y carrito
├── contacto/               # Formulario de contacto y correo
├── blog/                   # Blog de noticias o recetas
├── pedidos/                # Gestión de pedidos
└── carrito/                # Funcionalidades del carrito de compras

Funcionalidades principales

🏠 Página de inicio con presentación del negocio

🍰 Listado de productos y servicios con imágenes

🛒 Carrito de compras dinámico

📨 Formulario de contacto funcional con envío de correo

📝 Blog para publicaciones y artículos

⚙️ Panel administrativo completo de Django

🔐 Variables de entorno protegidas (.env)

🧾 Base de datos configurada con PostgreSQL


Autor:

Estiben De La Rosa
Desarrollador de Software Full Stack
📍 República Dominicana
GitHub: Estebin-77

Licencia
Este proyecto se distribuye bajo la licencia MIT.
Puedes usarlo, modificarlo y distribuirlo libremente con reconocimiento al autor original.