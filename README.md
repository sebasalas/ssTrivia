
# talaTrivia

**talaTrivia** es una aplicación de trivia desarrollada con Django y Django REST Framework. Permite a los usuarios participar en trivias, responder preguntas y ver rankings basados en sus puntuaciones. La aplicación utiliza Docker para facilitar su despliegue y gestión de dependencias.

## **Características**

- **Gestión de Usuarios:** Registro y autenticación.
- **Creación de Preguntas:** Administradores pueden crear y gestionar preguntas.
- **Creación de Trivias:** Administradores pueden crear y gestionar trivias.
- **Participación en Trivias:** Usuarios pueden responder preguntas y obtener puntajes.
- **Rankings:** Visualización de rankings de participantes.
- **Documentación de la API:** Acceso a través de Swagger y Redoc.
- **Colección de Postman:** Facilita las pruebas de la API.

## **Tecnologías**

- **Backend:** Python 3.9, Django, Django REST Framework
- **Base de Datos:** PostgreSQL
- **Contenedores:** Docker, Docker Compose
- **Formateo de Código:** Black

## **Instalación y Configuración**


### **1. Configurar Variables de Entorno**

Crear un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```env
DJANGO_SECRET_KEY=tu_clave_secreta_segura
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=talatrivia_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=tu_contraseña_segura
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

**Nota:** Reemplazar `tu_clave_secreta_segura` y `tu_contraseña_segura` con valores seguros.

### **2. Preparar la Base de Datos y Crear Superusuario**

Ejecutar los siguientes comandos para aplicar migraciones y crear un superusuario con las credenciales predeterminadas:

```bash
docker compose down -v && docker compose down --remove-orphans
```
```bash
docker compose run web python manage.py makemigrations && \ 
docker compose run web python manage.py migrate && \ 
docker compose run web python manage.py createsuperuser
```

Cuando se solicite, ingresar los siguientes datos para el superusuario:

- **Nombre de usuario:** admin
- **Email:** admin@example.com
- **Password:** administrador

### **3. Levantar los Servicios con Docker**

Construír y levantar los contenedores de Docker con el siguiente comando:

```bash
docker compose up --build
```

Esto iniciará los servicios necesarios y estará listo para recibir solicitudes.

## **Uso**

### **Probar la API con la Colección de Postman**

Para facilitar las pruebas de la API, se incluye una **colección de Postman** en la carpeta `postman`. Se debe utilizar de la siguente manera:

1. **Configurar Variables de Colección:**
   - En la colección **"talaTrivia"**, ir a **"Variables"**.
   - Ingresar el token JWT en las variables correspondientes (`admin_token` y `nuevo_usuario_token`).
2. **Ejecutar las Solicitudes:**
   - Seguir el orden de las solicitudes en la colección para probar todas las funcionalidades de la API.


## **Contacto**

Para consultas, contactar a [sebastiansalas@pm.me](mailto:sebastiansalas@pm.me)

