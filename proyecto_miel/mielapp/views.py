from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta
from .models import Usuario, Producto, Pedido, DetallePedido, Categoria
from .forms import (RegistroForm, LoginForm, PerfilForm, ProductoForm, 
                    PedidoForm, DetallePedidoForm, CategoriaForm)

from django.contrib.auth import update_session_auth_hash
from .forms import CustomPasswordChangeForm

# ============== DECORADORES ==============
def admin_required(view_func):
    """Decorador para verificar que el usuario sea administrador"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.rol != 'ADMIN':
            messages.error(request, 'No tienes permisos para acceder a esta página.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


# ============== AUTENTICACIÓN ==============
def login_view(request):
    """Vista de inicio de sesión"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.activo:
                    login(request, user)
                    messages.success(request, f'¡Bienvenido {user.first_name or user.username}!')
                    return redirect('home')
                else:
                    messages.error(request, 'Tu cuenta ha sido desactivada.')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    
    return render(request, 'mielapp/login.html', {'form': form})


def registro_view(request):
    """Vista de registro de usuarios"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.rol = 'CLIENTE'  # Por defecto todos son clientes
            user.save()
            messages.success(request, '¡Registro exitoso! Ahora puedes iniciar sesión.')
            return redirect('login')
    else:
        form = RegistroForm()
    
    return render(request, 'mielapp/registro.html', {'form': form})


@login_required
def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('login')


# ============== DASHBOARD ==============
@login_required
def home_view(request):
    """Vista del dashboard principal"""
    context = {}
    
    if request.user.rol == 'ADMIN':
        # Estadísticas para administradores
        hoy = timezone.now()
        inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Totales generales
        context['total_productos'] = Producto.objects.filter(activo=True).count()
        context['total_clientes'] = Usuario.objects.filter(rol='CLIENTE', activo=True).count()
        context['pedidos_pendientes'] = Pedido.objects.filter(estado='PENDIENTE').count()
        context['ventas_mes'] = Pedido.objects.filter(
            fecha_pedido__gte=inicio_mes
        ).aggregate(total=Sum('total'))['total'] or 0
        
        # Productos más vendidos
        context['productos_top'] = Producto.objects.annotate(
            vendidos=Sum('detallepedido__cantidad')
        ).order_by('-vendidos')[:5]
        
        # Últimos pedidos
        context['ultimos_pedidos'] = Pedido.objects.select_related('cliente').order_by('-fecha_pedido')[:10]
        
        # Productos con stock bajo (menos de 10 unidades)
        context['productos_stock_bajo'] = Producto.objects.filter(
            activo=True, stock__lt=10
        ).order_by('stock')[:5]
        
        # Datos para gráficos (últimos 6 meses)
        meses_datos = []
        for i in range(6):
            mes = hoy - timedelta(days=30*i)
            inicio = mes.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if i == 0:
                fin = hoy
            else:
                fin = inicio + timedelta(days=32)
                fin = fin.replace(day=1) - timedelta(seconds=1)
            
            ventas = Pedido.objects.filter(
                fecha_pedido__gte=inicio,
                fecha_pedido__lte=fin
            ).aggregate(total=Sum('total'))['total'] or 0
            
            meses_datos.insert(0, {
                'mes': inicio.strftime('%B'),
                'ventas': float(ventas)
            })
        
        context['datos_grafico'] = meses_datos
        
    else:
        # Dashboard para clientes
        context['mis_pedidos'] = Pedido.objects.filter(
            cliente=request.user
        ).order_by('-fecha_pedido')[:5]
        
        context['productos_destacados'] = Producto.objects.filter(
            activo=True
        ).order_by('-fecha_creacion')[:6]
    
    return render(request, 'mielapp/home.html', context)

# ============== PRODUCTOS ==============
@login_required
def productos_view(request):
    """Vista para listar productos"""
    productos = Producto.objects.select_related('categoria').all()
    
    # Filtros
    busqueda = request.GET.get('buscar', '')
    categoria_id = request.GET.get('categoria', '')
    
    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) | 
            Q(descripcion__icontains=busqueda)
        )
    
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    categorias = Categoria.objects.all()
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'busqueda': busqueda,
        'categoria_seleccionada': categoria_id
    }
    return render(request, 'mielapp/productos.html', context)


@login_required
@admin_required
def crear_producto_view(request):
    """Vista para crear un nuevo producto"""
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f'Producto "{producto.nombre}" creado exitosamente.')
            return redirect('productos')
    else:
        form = ProductoForm()
    
    return render(request, 'mielapp/crear_producto.html', {'form': form})


@login_required
@admin_required
def editar_producto_view(request, pk):
    """Vista para editar un producto existente"""
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f'Producto "{producto.nombre}" actualizado correctamente.')
            return redirect('productos')
    else:
        form = ProductoForm(instance=producto)
    
    context = {
        'form': form,
        'producto': producto,
        'editar': True
    }
    return render(request, 'mielapp/crear_producto.html', context)


@login_required
@admin_required
def eliminar_producto_view(request, pk):
    """Vista para eliminar (desactivar) un producto"""
    producto = get_object_or_404(Producto, pk=pk)
    producto.activo = False
    producto.save()
    messages.success(request, f'Producto "{producto.nombre}" desactivado correctamente.')
    return redirect('productos')


@login_required
def detalle_producto_view(request, pk):
    """Vista para ver detalles de un producto"""
    producto = get_object_or_404(Producto, pk=pk)
    productos_relacionados = Producto.objects.filter(
        categoria=producto.categoria,
        activo=True
    ).exclude(pk=pk)[:4]
    
    context = {
        'producto': producto,
        'productos_relacionados': productos_relacionados
    }
    return render(request, 'mielapp/detalle_producto.html', context)


# ============== CATEGORÍAS ==============
@login_required
@admin_required
def categorias_view(request):
    """Vista para gestionar categorías"""
    categorias = Categoria.objects.annotate(
        num_productos=Count('productos')
    ).all()
    
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoría "{categoria.nombre}" creada exitosamente.')
            return redirect('categorias')
    else:
        form = CategoriaForm()
    
    context = {
        'categorias': categorias,
        'form': form
    }
    return render(request, 'mielapp/categorias.html', context)


@login_required
@admin_required
def editar_categoria_view(request, pk):
    """Vista para editar una categoría"""
    categoria = get_object_or_404(Categoria, pk=pk)
    
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, f'Categoría "{categoria.nombre}" actualizada correctamente.')
            return redirect('categorias')
    else:
        form = CategoriaForm(instance=categoria)
    
    context = {
        'form': form,
        'categoria': categoria
    }
    return render(request, 'mielapp/editar_categoria.html', context)


@login_required
@admin_required
def eliminar_categoria_view(request, pk):
    """Vista para eliminar una categoría"""
    categoria = get_object_or_404(Categoria, pk=pk)
    nombre = categoria.nombre
    categoria.delete()
    messages.success(request, f'Categoría "{nombre}" eliminada correctamente.')
    return redirect('categorias')

# ============== PEDIDOS ==============
@login_required
def pedidos_view(request):
    """Vista para listar pedidos"""
    if request.user.rol == 'ADMIN':
        pedidos = Pedido.objects.select_related('cliente').prefetch_related('detalles').all()
    else:
        pedidos = Pedido.objects.filter(cliente=request.user).prefetch_related('detalles').all()
    
    # Filtros
    estado = request.GET.get('estado', '')
    if estado:
        pedidos = pedidos.filter(estado=estado)
    
    context = {
        'pedidos': pedidos,
        'estado_seleccionado': estado,
        'estados': Pedido.ESTADOS
    }
    return render(request, 'mielapp/pedidos.html', context)


@login_required
def detalle_pedido_view(request, pk):
    """Vista para ver detalles de un pedido"""
    if request.user.rol == 'ADMIN':
        pedido = get_object_or_404(Pedido, pk=pk)
    else:
        pedido = get_object_or_404(Pedido, pk=pk, cliente=request.user)
    
    detalles = pedido.detalles.select_related('producto').all()
    
    context = {
        'pedido': pedido,
        'detalles': detalles
    }
    return render(request, 'mielapp/detalle_pedido.html', context)


@login_required
@admin_required
def crear_pedido_view(request):
    """Vista para crear un nuevo pedido"""
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            pedido = form.save()
            messages.success(request, f'Pedido #{pedido.id} creado exitosamente.')
            return redirect('agregar_productos_pedido', pk=pedido.id)
    else:
        form = PedidoForm()
    
    return render(request, 'mielapp/crear_pedido.html', {'form': form})


@login_required
@admin_required
def agregar_productos_pedido_view(request, pk):
    """Vista para agregar productos a un pedido"""
    pedido = get_object_or_404(Pedido, pk=pk)
    
    if request.method == 'POST':
        form = DetallePedidoForm(request.POST)
        if form.is_valid():
            detalle = form.save(commit=False)
            detalle.pedido = pedido
            detalle.save()
            pedido.calcular_total()
            messages.success(request, f'Producto agregado al pedido.')
            return redirect('agregar_productos_pedido', pk=pk)
    else:
        form = DetallePedidoForm()
    
    detalles = pedido.detalles.select_related('producto').all()
    
    context = {
        'pedido': pedido,
        'form': form,
        'detalles': detalles
    }
    return render(request, 'mielapp/agregar_productos_pedido.html', context)


@login_required
@admin_required
def actualizar_estado_pedido_view(request, pk):
    """Vista para actualizar el estado de un pedido"""
    pedido = get_object_or_404(Pedido, pk=pk)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Pedido.ESTADOS):
            pedido.estado = nuevo_estado
            pedido.save()
            messages.success(request, f'Estado del pedido actualizado a {pedido.get_estado_display()}.')
    
    return redirect('detalle_pedido', pk=pk)


@login_required
@admin_required
def eliminar_detalle_pedido_view(request, pk):
    """Vista para eliminar un detalle de pedido"""
    detalle = get_object_or_404(DetallePedido, pk=pk)
    pedido = detalle.pedido
    detalle.delete()
    pedido.calcular_total()
    messages.success(request, 'Producto eliminado del pedido.')
    return redirect('agregar_productos_pedido', pk=pedido.id)


# ============== CLIENTES ==============
@login_required
@admin_required
def clientes_view(request):
    """Vista para listar clientes"""
    clientes = Usuario.objects.filter(rol='CLIENTE').annotate(
        total_pedidos=Count('pedidos'),
        total_gastado=Sum('pedidos__total')
    ).order_by('-fecha_registro')
    
    # Búsqueda
    busqueda = request.GET.get('buscar', '')
    if busqueda:
        clientes = clientes.filter(
            Q(username__icontains=busqueda) |
            Q(first_name__icontains=busqueda) |
            Q(last_name__icontains=busqueda) |
            Q(email__icontains=busqueda)
        )
    
    context = {
        'clientes': clientes,
        'busqueda': busqueda
    }
    return render(request, 'mielapp/clientes.html', context)


@login_required
@admin_required
def detalle_cliente_view(request, pk):
    """Vista para ver detalles de un cliente"""
    cliente = get_object_or_404(Usuario, pk=pk, rol='CLIENTE')
    pedidos = Pedido.objects.filter(cliente=cliente).order_by('-fecha_pedido')[:10]
    
    stats = {
        'total_pedidos': Pedido.objects.filter(cliente=cliente).count(),
        'total_gastado': Pedido.objects.filter(cliente=cliente).aggregate(
            total=Sum('total'))['total'] or 0,
        'pedidos_pendientes': Pedido.objects.filter(
            cliente=cliente, estado='PENDIENTE').count()
    }
    
    context = {
        'cliente': cliente,
        'pedidos': pedidos,
        'stats': stats
    }
    return render(request, 'mielapp/detalle_cliente.html', context)


@login_required
@admin_required
def toggle_cliente_activo_view(request, pk):
    """Vista para activar/desactivar un cliente"""
    cliente = get_object_or_404(Usuario, pk=pk, rol='CLIENTE')
    cliente.activo = not cliente.activo
    cliente.save()
    
    estado = "activado" if cliente.activo else "desactivado"
    messages.success(request, f'Cliente {cliente.username} {estado} correctamente.')
    return redirect('clientes')


# ============== PERFIL ==============
@login_required
def perfil_view(request):
    """Vista para ver y editar perfil del usuario"""
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('perfil')
    else:
        form = PerfilForm(instance=request.user)
    
    # Estadísticas del usuario
    if request.user.rol == 'CLIENTE':
        stats = {
            'total_pedidos': Pedido.objects.filter(cliente=request.user).count(),
            'total_gastado': Pedido.objects.filter(cliente=request.user).aggregate(
                total=Sum('total'))['total'] or 0,
            'pedidos_pendientes': Pedido.objects.filter(
                cliente=request.user, estado='PENDIENTE').count()
        }
    else:
        stats = None
    
    context = {
        'form': form,
        'stats': stats
    }
    return render(request, 'mielapp/perfil.html', context)


@login_required
def cambiar_password_view(request):
    """Vista para cambiar contraseña"""
    if request.method == 'POST':
        password_actual = request.POST.get('password_actual')
        password_nueva = request.POST.get('password_nueva')
        password_confirmacion = request.POST.get('password_confirmacion')
        
        if not request.user.check_password(password_actual):
            messages.error(request, 'La contraseña actual es incorrecta.')
        elif password_nueva != password_confirmacion:
            messages.error(request, 'Las contraseñas nuevas no coinciden.')
        elif len(password_nueva) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
        else:
            request.user.set_password(password_nueva)
            request.user.save()
            messages.success(request, 'Contraseña cambiada correctamente. Por favor, inicia sesión nuevamente.')
            return redirect('login')
    
    return render(request, 'mielapp/cambiar_password.html')

# ============== REPORTES ==============
from django.http import JsonResponse

@login_required
@admin_required
def reportes_view(request):
    """Vista para reportes y estadísticas"""
    hoy = timezone.now()
    inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    inicio_año = hoy.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Ventas por mes (últimos 12 meses)
    ventas_mensuales = []
    for i in range(12):
        mes = hoy - timedelta(days=30*i)
        inicio = mes.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if i == 0:
            fin = hoy
        else:
            fin = inicio + timedelta(days=32)
            fin = fin.replace(day=1) - timedelta(seconds=1)
        
        ventas = Pedido.objects.filter(
            fecha_pedido__gte=inicio,
            fecha_pedido__lte=fin,
            estado__in=['PROCESANDO', 'ENVIADO', 'ENTREGADO']
        ).aggregate(
            total=Sum('total'),
            cantidad=Count('id')
        )
        
        ventas_mensuales.insert(0, {
            'mes': inicio.strftime('%b %Y'),
            'total': float(ventas['total'] or 0),
            'cantidad': ventas['cantidad'] or 0
        })
    
    # Productos más vendidos
    productos_top = Producto.objects.annotate(
        total_vendido=Sum('detallepedido__cantidad'),
        ingresos=Sum(F('detallepedido__cantidad') * F('detallepedido__precio_unitario'))
    ).filter(total_vendido__isnull=False).order_by('-total_vendido')[:10]
    
    # Ventas por categoría
    ventas_categorias = Categoria.objects.annotate(
        total_vendido=Sum(
            F('productos__detallepedido__cantidad') * 
            F('productos__detallepedido__precio_unitario')
        )
    ).filter(total_vendido__isnull=False).order_by('-total_vendido')
    
    # Clientes top
    clientes_top = Usuario.objects.filter(rol='CLIENTE').annotate(
        total_compras=Sum('pedidos__total'),
        num_pedidos=Count('pedidos')
    ).filter(total_compras__isnull=False).order_by('-total_compras')[:10]
    
    # Resumen general
    resumen = {
        'ventas_mes': Pedido.objects.filter(
            fecha_pedido__gte=inicio_mes,
            estado__in=['PROCESANDO', 'ENVIADO', 'ENTREGADO']
        ).aggregate(total=Sum('total'))['total'] or 0,
        
        'ventas_año': Pedido.objects.filter(
            fecha_pedido__gte=inicio_año,
            estado__in=['PROCESANDO', 'ENVIADO', 'ENTREGADO']
        ).aggregate(total=Sum('total'))['total'] or 0,
        
        'pedidos_mes': Pedido.objects.filter(
            fecha_pedido__gte=inicio_mes
        ).count(),
        
        'clientes_nuevos_mes': Usuario.objects.filter(
            rol='CLIENTE',
            fecha_registro__gte=inicio_mes
        ).count(),
        
        'productos_activos': Producto.objects.filter(activo=True).count(),
        
        'stock_total': Producto.objects.filter(activo=True).aggregate(
            total=Sum('stock'))['total'] or 0,
    }
    
    context = {
        'ventas_mensuales': ventas_mensuales,
        'productos_top': productos_top,
        'ventas_categorias': ventas_categorias,
        'clientes_top': clientes_top,
        'resumen': resumen
    }
    
    return render(request, 'mielapp/reportes.html', context)


@login_required
@admin_required
def datos_grafico_ventas(request):
    """API para obtener datos de ventas para gráficos"""
    periodo = request.GET.get('periodo', 'mes')  # mes, año
    hoy = timezone.now()
    
    if periodo == 'mes':
        dias = 30
        formato = '%d/%m'
    else:
        dias = 365
        formato = '%b'
    
    datos = []
    for i in range(dias if periodo == 'mes' else 12):
        if periodo == 'mes':
            fecha = hoy - timedelta(days=i)
            inicio = fecha.replace(hour=0, minute=0, second=0, microsecond=0)
            fin = fecha.replace(hour=23, minute=59, second=59, microsecond=999999)
        else:
            fecha = hoy - timedelta(days=30*i)
            inicio = fecha.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            fin = (inicio + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        
        ventas = Pedido.objects.filter(
            fecha_pedido__gte=inicio,
            fecha_pedido__lte=fin,
            estado__in=['PROCESANDO', 'ENVIADO', 'ENTREGADO']
        ).aggregate(total=Sum('total'))['total'] or 0
        
        datos.insert(0, {
            'fecha': inicio.strftime(formato),
            'ventas': float(ventas)
        })
    
    return JsonResponse({'datos': datos})

@login_required
def cambiar_password_view(request):
    if request.method == "POST":
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # mantiene al usuario logueado
            messages.success(request, "Contraseña actualizada correctamente.")
            return redirect('perfil')  # o a donde quieras
    else:
        form = CustomPasswordChangeForm(user=request.user)
    
    return render(request, "mielapp/cambiar_password.html", {"form": form})


# ============== CARRITO DE COMPRAS ==============
@login_required
def agregar_al_carrito_view(request, producto_id):
    """Agregar producto al carrito"""
    from .models import Carrito
    
    producto = get_object_or_404(Producto, pk=producto_id, activo=True)
    
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        
        # Verificar stock disponible
        if cantidad > producto.stock:
            messages.error(request, f'Solo hay {producto.stock} unidades disponibles.')
            return redirect('productos')
        
        # Verificar si ya existe en el carrito
        carrito_item, created = Carrito.objects.get_or_create(
            usuario=request.user,
            producto=producto,
            defaults={'cantidad': cantidad}
        )
        
        if not created:
            # Si ya existe, actualizar cantidad
            nueva_cantidad = carrito_item.cantidad + cantidad
            if nueva_cantidad > producto.stock:
                messages.error(request, f'Solo hay {producto.stock} unidades disponibles.')
            else:
                carrito_item.cantidad = nueva_cantidad
                carrito_item.save()
                messages.success(request, f'Cantidad actualizada: {producto.nombre}')
        else:
            messages.success(request, f'Producto agregado al carrito: {producto.nombre}')
    
    return redirect('ver_carrito')


@login_required
def ver_carrito_view(request):
    """Ver carrito de compras"""
    from .models import Carrito
    
    items_carrito = Carrito.objects.filter(usuario=request.user).select_related('producto')
    
    total = sum(item.subtotal for item in items_carrito)
    
    context = {
        'items_carrito': items_carrito,
        'total': total
    }
    
    return render(request, 'mielapp/carrito.html', context)


@login_required
def actualizar_carrito_view(request, item_id):
    """Actualizar cantidad en el carrito"""
    from .models import Carrito
    
    item = get_object_or_404(Carrito, pk=item_id, usuario=request.user)
    
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        
        if cantidad > item.producto.stock:
            messages.error(request, f'Solo hay {item.producto.stock} unidades disponibles.')
        elif cantidad < 1:
            messages.error(request, 'La cantidad debe ser mayor a 0.')
        else:
            item.cantidad = cantidad
            item.save()
            messages.success(request, 'Cantidad actualizada correctamente.')
    
    return redirect('ver_carrito')


@login_required
def eliminar_del_carrito_view(request, item_id):
    """Eliminar producto del carrito"""
    from .models import Carrito
    
    item = get_object_or_404(Carrito, pk=item_id, usuario=request.user)
    nombre_producto = item.producto.nombre
    item.delete()
    
    messages.success(request, f'Producto eliminado del carrito: {nombre_producto}')
    return redirect('ver_carrito')


@login_required
def vaciar_carrito_view(request):
    """Vaciar todo el carrito"""
    from .models import Carrito
    
    Carrito.objects.filter(usuario=request.user).delete()
    messages.info(request, 'Carrito vaciado correctamente.')
    return redirect('ver_carrito')


@login_required
def finalizar_compra_view(request):
    """Crear pedido desde el carrito"""
    from .models import Carrito
    
    items_carrito = Carrito.objects.filter(usuario=request.user).select_related('producto')
    
    if not items_carrito.exists():
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('productos')
    
    # Verificar stock disponible
    for item in items_carrito:
        if item.cantidad > item.producto.stock:
            messages.error(request, f'No hay suficiente stock de {item.producto.nombre}')
            return redirect('ver_carrito')
    
    if request.method == 'POST':
        direccion_envio = request.POST.get('direccion_envio', request.user.direccion or '')
        notas = request.POST.get('notas', '')
        
        if not direccion_envio:
            messages.error(request, 'Debes proporcionar una dirección de envío.')
            return redirect('ver_carrito')
        
        # Crear el pedido
        pedido = Pedido.objects.create(
            cliente=request.user,
            estado='PENDIENTE',
            direccion_envio=direccion_envio,
            notas=notas
        )
        
        # Crear detalles del pedido y actualizar stock
        for item in items_carrito:
            DetallePedido.objects.create(
                pedido=pedido,
                producto=item.producto,
                cantidad=item.cantidad,
                precio_unitario=item.producto.precio
            )
            
            # Reducir stock
            item.producto.stock -= item.cantidad
            item.producto.save()
        
        # Calcular total del pedido
        pedido.calcular_total()
        
        # Vaciar el carrito
        items_carrito.delete()
        
        messages.success(request, f'¡Pedido #{pedido.id} creado exitosamente!')
        return redirect('detalle_pedido', pk=pedido.id)
    
    # Mostrar formulario de confirmación
    total = sum(item.subtotal for item in items_carrito)
    
    context = {
        'items_carrito': items_carrito,
        'total': total,
        'direccion_usuario': request.user.direccion or ''
    }
    
    return render(request, 'mielapp/finalizar_compra.html', context)