from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    
    # Productos
    path('productos/', views.productos_view, name='productos'),
    path('productos/crear/', views.crear_producto_view, name='crear_producto'),
    path('productos/<int:pk>/editar/', views.editar_producto_view, name='editar_producto'),
    path('productos/<int:pk>/eliminar/', views.eliminar_producto_view, name='eliminar_producto'),
    path('productos/<int:pk>/', views.detalle_producto_view, name='detalle_producto'),
    
    # Categorías
    path('categorias/', views.categorias_view, name='categorias'),
    path('categorias/<int:pk>/editar/', views.editar_categoria_view, name='editar_categoria'),
    path('categorias/<int:pk>/eliminar/', views.eliminar_categoria_view, name='eliminar_categoria'),
    
    # Pedidos
    path('pedidos/', views.pedidos_view, name='pedidos'),
    path('pedidos/crear/', views.crear_pedido_view, name='crear_pedido'),
    path('pedidos/<int:pk>/', views.detalle_pedido_view, name='detalle_pedido'),
    path('pedidos/<int:pk>/agregar-productos/', views.agregar_productos_pedido_view, name='agregar_productos_pedido'),
    path('pedidos/<int:pk>/actualizar-estado/', views.actualizar_estado_pedido_view, name='actualizar_estado_pedido'),
    path('pedidos/detalle/<int:pk>/eliminar/', views.eliminar_detalle_pedido_view, name='eliminar_detalle_pedido'),
    
    # Clientes
    path('clientes/', views.clientes_view, name='clientes'),
    path('clientes/<int:pk>/', views.detalle_cliente_view, name='detalle_cliente'),
    path('clientes/<int:pk>/toggle-activo/', views.toggle_cliente_activo_view, name='toggle_cliente_activo'),
    
    # Perfil
    path('perfil/', views.perfil_view, name='perfil'),
    path('perfil/cambiar-password/', views.cambiar_password_view, name='cambiar_password'),
    
    # Reportes
    path('reportes/', views.reportes_view, name='reportes'),
    path('api/datos-grafico-ventas/', views.datos_grafico_ventas, name='datos_grafico_ventas'),
    
    # Carrito de compras
    path('carrito/', views.ver_carrito_view, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito_view, name='agregar_al_carrito'),
    path('carrito/actualizar/<int:item_id>/', views.actualizar_carrito_view, name='actualizar_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_del_carrito_view, name='eliminar_del_carrito'),
    path('carrito/vaciar/', views.vaciar_carrito_view, name='vaciar_carrito'),
    path('carrito/finalizar/', views.finalizar_compra_view, name='finalizar_compra'),
]