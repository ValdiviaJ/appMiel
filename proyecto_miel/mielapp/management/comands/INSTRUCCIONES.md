# 🚀 GUÍA PASO A PASO PARA EJECUTAR EL PROYECTO

## ✅ PASO 1: Verificar Python instalado

Abre una terminal/CMD y ejecuta:
```bash
python --version
```

Deberías ver algo como: `Python 3.10.x` o superior.

Si no tienes Python instalado, descárgalo de: https://www.python.org/downloads/

---

## 📁 PASO 2: Crear la estructura del proyecto

### Opción A: Crear carpetas manualmente

```bash
# Crear carpeta principal
mkdir proyecto_miel
cd proyecto_miel

# Crear estructura de Django
django-admin startproject proyecto_miel .
python manage.py startapp mielapp

# Crear carpetas necesarias
mkdir -p mielapp/templates/mielapp
mkdir -p mielapp/static/mielapp/css
mkdir -p mielapp/static/mielapp/js
mkdir -p mielapp/static/mielapp/img
mkdir -p mielapp/management/commands
mkdir -p media/productos
mkdir -p media/usuarios
```

### Opción B: Usar comandos de Django

```bash
# Instalar Django primero
pip install django pillow

# Crear proyecto
django-admin startproject proyecto_miel
cd proyecto_miel

# Crear app
python manage.py startapp mielapp
```

---

## 📝 PASO 3: Copiar los archivos del código

Copia cada archivo que te he proporcionado en su ubicación correspondiente:

### Archivos principales:
- `proyecto_miel/settings.py`
- `proyecto_miel/urls.py`
- `mielapp/models.py`
- `mielapp/views.py` (partes 1, 2, 3 y 4 - unirlas en un solo archivo)
- `mielapp/forms.py`
- `mielapp/urls.py`
- `mielapp/admin.py`

### Comando de gestión:
- `mielapp/management/__init__.py` (archivo vacío)
- `mielapp/management/commands/__init__.py` (archivo vacío)
- `mielapp/management/commands/cargar_datos.py`

### Templates (en `mielapp/templates/mielapp/`):
- `base.html`
- `home.html`
- `login.html`
- `registro.html`
- `productos.html`
- `crear_producto.html`
- `detalle_producto.html`
- `pedidos.html`
- `detalle_pedido.html`
- `crear_pedido.html`
- `agregar_productos_pedido.html`
- `clientes.html`
- `detalle_cliente.html`
- `categorias.html`
- `editar_categoria.html`
- `perfil.html`
- `cambiar_password.html`
- `reportes.html`

---

## 🔧 PASO 4: Crear entorno virtual (RECOMENDADO)

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate

# En Linux/Mac:
source venv/bin/activate
```

Verás `(venv)` al inicio de tu línea de comandos.

---

## 📦 PASO 5: Instalar dependencias

```bash
pip install django pillow
```

**Dependencias instaladas:**
- `django` - Framework web
- `pillow` - Manejo de imágenes

---

## 🗄️ PASO 6: Crear la base de datos

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate
```

Deberías ver mensajes como:
```
Migrations for 'mielapp':
  mielapp/migrations/0001_initial.py
    - Create model Usuario
    - Create model Categoria
    - Create model Producto
    ...

Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
```

---

## 🎲 PASO 7: Cargar datos de prueba

```bash
python manage.py cargar_datos
```

Este comando creará:
- ✅ Usuario administrador: `admin` / `admin123`
- ✅ 3 clientes de prueba: `cliente1`, `cliente2`, `cliente3` / `cliente123`
- ✅ 5 categorías de productos
- ✅ 8 productos de ejemplo
- ✅ 10 pedidos de prueba

---

## 🚀 PASO 8: Ejecutar el servidor

### Para acceso local (solo desde tu PC):
```bash
python manage.py runserver
```

Accede desde: http://localhost:8000

### Para acceso desde red local (celular/tablet):
```bash
python manage.py runserver 0.0.0.0:8000
```

#### Obtener tu IP local:

**Windows:**
```bash
ipconfig
```
Busca: `Dirección IPv4. . . . . . . . . . . . . . : 192.168.X.X`

**Linux/Mac:**
```bash
ifconfig
# o
ip addr show
```

Accede desde tu celular: `http://192.168.X.X:8000`

---

## 🔐 PASO 9: Iniciar sesión

### Como Administrador:
- Usuario: `admin`
- Contraseña: `admin123`

### Como Cliente:
- Usuario: `cliente1`, `cliente2` o `cliente3`
- Contraseña: `cliente123`

---

## 🎯 VERIFICAR QUE TODO FUNCIONA

### ✅ Checklist:

1. ☑️ La página de login se carga correctamente
2. ☑️ Puedes iniciar sesión con `admin/admin123`
3. ☑️ El dashboard muestra estadísticas
4. ☑️ Puedes ver la lista de productos (deberían haber 8)
5. ☑️ Puedes crear un nuevo producto
6. ☑️ Puedes ver los pedidos
7. ☑️ Los gráficos se muestran correctamente
8. ☑️ Puedes cambiar tu contraseña
9. ☑️ Puedes cerrar sesión

---

## ⚠️ SOLUCIÓN DE PROBLEMAS COMUNES

### Error: "No module named 'PIL'"
```bash
pip install pillow
```

### Error: "Table doesn't exist"
```bash
python manage.py makemigrations
python manage.py migrate
```

### Error: "Port is already in use"
```bash
# Usar otro puerto
python manage.py runserver 8001
```

### Las imágenes no se cargan
Verifica que en `settings.py` esté:
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

Y en `urls.py` principal:
```python
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### No puedo acceder desde el celular
1. Asegúrate de estar en la misma red WiFi
2. Verifica que tu firewall no bloquee el puerto 8000
3. Usa la IP correcta (verifica con `ipconfig` o `ifconfig`)
4. Ejecuta con: `python manage.py runserver 0.0.0.0:8000`

---

## 🎨 PERSONALIZACIÓN

### Cambiar colores del tema
Edita en `base.html` las variables CSS:
```css
:root {
    --primary-color: #f39c12;  /* Color principal */
    --secondary-color: #e67e22; /* Color secundario */
}
```

### Agregar más productos
1. Inicia sesión como admin
2. Ve a "Productos"
3. Clic en "Nuevo Producto"
4. Llena el formulario y guarda

### Crear más categorías
1. Inicia sesión como admin
2. Ve a "Categorías"
3. Llena el formulario en el panel izquierdo
4. Clic en "Crear Categoría"

---

## 📊 ACCESO AL PANEL DE ADMINISTRACIÓN DE DJANGO

```bash
http://localhost:8000/admin
```

Usuario: `admin` / `admin123`

Desde aquí puedes gestionar todo manualmente:
- Usuarios
- Productos
- Pedidos
- Categorías

---

## 🛑 DETENER EL SERVIDOR

Presiona `Ctrl + C` en la terminal donde está corriendo el servidor.

---

## 🔄 REINICIAR LA BASE DE DATOS

Si quieres empezar de cero:

```bash
# Eliminar base de datos
del db.sqlite3  # Windows
rm db.sqlite3   # Linux/Mac

# Recrear
python manage.py migrate
python manage.py cargar_datos
```

---

## 📞 SOPORTE

Si tienes problemas:
1. Verifica que todos los archivos estén en las carpetas correctas
2. Asegúrate de tener las dependencias instaladas
3. Revisa los mensajes de error en la terminal
4. Verifica que el puerto 8000 esté disponible

---

**¡Listo! Tu aplicación de venta de miel está funcionando! 🍯**