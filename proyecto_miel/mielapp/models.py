from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from decimal import Decimal

class Usuario(AbstractUser):
    """Modelo de usuario personalizado con roles"""
    ROLES = (
        ('ADMIN', 'Administrador'),
        ('CLIENTE', 'Cliente'),
    )
    
    rol = models.CharField(max_length=10, choices=ROLES, default='CLIENTE')
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    imagen = models.ImageField(upload_to='usuarios/', blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"


class Categoria(models.Model):
    """Categorías de productos"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """Productos de miel y derivados"""
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='productos'
    )
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return self.nombre
    
    @property
    def disponible(self):
        return self.activo and self.stock > 0


class Pedido(models.Model):
    """Pedidos realizados por los clientes"""
    ESTADOS = (
        ('PENDIENTE', 'Pendiente'),
        ('PROCESANDO', 'Procesando'),
        ('ENVIADO', 'Enviado'),
        ('ENTREGADO', 'Entregado'),
        ('CANCELADO', 'Cancelado'),
    )
    
    cliente = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE,
        related_name='pedidos'
    )
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=15, choices=ESTADOS, default='PENDIENTE')
    total = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0
    )
    direccion_envio = models.TextField()
    notas = models.TextField(blank=True, null=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-fecha_pedido']
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.username}"
    
    def calcular_total(self):
        """Calcula el total del pedido sumando los detalles"""
        total = sum(detalle.subtotal for detalle in self.detalles.all())
        self.total = total
        self.save()
        return total


class DetallePedido(models.Model):
    """Detalles de los productos en cada pedido"""
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE
    )
    cantidad = models.IntegerField(
        validators=[MinValueValidator(1)]
    )
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    
    class Meta:
        verbose_name = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedidos'
    
    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"
    
    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario
    
    def save(self, *args, **kwargs):
        # Si no se especifica precio_unitario, tomar el del producto
        if not self.precio_unitario:
            self.precio_unitario = self.producto.precio
        super().save(*args, **kwargs)


class Carrito(models.Model):
    """Carrito de compras del usuario"""
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='carrito'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE
    )
    cantidad = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Item del Carrito'
        verbose_name_plural = 'Items del Carrito'
        unique_together = ['usuario', 'producto']  # Un producto por usuario en el carrito
    
    def __str__(self):
        return f"{self.usuario.username} - {self.producto.nombre} ({self.cantidad})"
    
    @property
    def subtotal(self):
        return self.cantidad * self.producto.precio