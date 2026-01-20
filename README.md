# DulceCayenaWeb

DulceCayenaWeb es una aplicación web full-stack desarrollada con Django y PostgreSQL para una repostería artesanal.  
El proyecto está diseñado con enfoque en arquitectura limpia, buenas prácticas y preparación para producción.

---

## Descripción

La aplicación permite gestionar productos, pedidos, publicaciones de blog, contacto con clientes y facturación en PDF, ofreciendo una experiencia moderna, clara y funcional.

Este proyecto forma parte de mi portafolio profesional como desarrollador de software.

---

## Funcionalidades

- Catálogo de productos y servicios
- Carrito de compras dinámico
- Gestión de pedidos
- Blog de publicaciones
- Formulario de contacto con envío de correo
- Generación de facturas PDF
- Panel administrativo Django
- Variables de entorno seguras
- Base de datos PostgreSQL

---

## Tecnologías utilizadas

- Python 3.10+
- Django 5.2
- PostgreSQL
- HTML5 / CSS3 / Bootstrap
- JavaScript ES6
- Git y GitHub
- python-dotenv

---

## Estructura del proyecto

DulceCayenaWeb/
│
├── ProyectoDulceCayena/
├── inicio/
├── servicios/
├── tienda/
├── contacto/
├── blog/
├── pedidos/
├── carrito/
├── manage.py
├── requirements.txt
└── README.md

---

## Instalación local

Clonar el repositorio:

git clone https://github.com/Estebin-77/DulceCayenaWeb.git  
cd DulceCayenaWeb  

Crear entorno virtual:

python -m venv venv  
venv\Scripts\activate  

Instalar dependencias:

pip install -r requirements.txt  

Migraciones:

python manage.py migrate  

Ejecutar servidor:

python manage.py runserver  

---

## Variables de entorno

Archivo .env:

SECRET_KEY=tu_secret_key  
DEBUG=True  
ALLOWED_HOSTS=127.0.0.1,localhost  

DB_NAME=dulcecayena  
DB_USER=postgres  
DB_PASSWORD=tu_password  
DB_HOST=localhost  
DB_PORT=5432  

---

## Enfoque del proyecto

Este proyecto fue desarrollado aplicando:

- Arquitectura clara
- Código mantenible
- Buenas prácticas Django
- Seguridad con variables de entorno
- Control de versiones profesional
- Preparación para despliegue en producción

---

## Roadmap

- Despliegue en producción
- Autenticación de usuarios
- Dashboard administrativo personalizado
- Pasarela de pagos
- Optimización SEO

---

## Autor

Estiben De La Rosa  
Desarrollador de Software Full Stack  
República Dominicana  

GitHub: https://github.com/Estebin-77  

---

## Licencia

Este proyecto se distribuye bajo la licencia MIT.
