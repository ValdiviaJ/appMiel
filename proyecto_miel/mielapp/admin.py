from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Categoria, Producto, Pedido, DetallePedido, Carrito


# ======================
# USUARIO
# ======================
@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'rol', 'activo']
    list_filter = ['rol', 'activo', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {'fields': ('rol', 'telefono', 'direccion', 'imagen', 'activo')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Adicional', {'fields': ('rol', 'telefono', 'direccion', 'imagen')}),
    )


# ======================
# CATEGORÍA
# ======================
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'fecha_creacion']
    search_fields = ['nombre']


# ======================
# PRODUCTO
# ======================
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'precio', 'stock', 'activo', 'fecha_creacion']
    list_filter = ['activo', 'categoria', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['precio', 'stock', 'activo']


# ======================
# DETALLE DE PEDIDO INLINE
# ======================
class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1


# ======================
# PEDIDO
# ======================
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'fecha_pedido', 'estado', 'total']
    list_filter = ['estado', 'fecha_pedido']
    search_fields = ['cliente__username', 'cliente__email']
    inlines = [DetallePedidoInline]
    readonly_fields = ['total']


# ======================
# DETALLE PEDIDO
# ======================
@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'producto', 'cantidad', 'precio_unitario', 'subtotal']
    list_filter = ['pedido__fecha_pedido']


# ======================
# CARRITO
# ======================
@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'producto', 'cantidad', 'subtotal', 'fecha_agregado']
    list_filter = ['fecha_agregado']
    search_fields = ['usuario__username', 'producto__nombre']
    readonly_fields = ['fecha_agregado']

    fieldsets = (
        (None, {
            'fields': ('usuario', 'producto', 'cantidad', 'subtotal', 'fecha_agregado')
        }),
    )
