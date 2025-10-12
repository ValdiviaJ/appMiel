from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from mielapp.models import Categoria, Producto, Pedido, DetallePedido
from decimal import Decimal
import random

Usuario = get_user_model()

class Command(BaseCommand):
    help = 'Carga datos de prueba para la aplicación de miel'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando carga de datos de prueba...'))
        
        # Crear superusuario admin
        if not Usuario.objects.filter(username='admin').exists():
            admin = Usuario.objects.create_superuser(
                username='admin',
                email='admin@mielapp.com',
                password='admin123',
                first_name='Administrador',
                last_name='Sistema',
                rol='ADMIN'
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Admin creado: admin/admin123'))
        
        # Crear clientes de prueba
        clientes_data = [
            {'username': 'cliente1', 'email': 'cliente1@mail.com', 'first_name': 'Juan', 'last_name': 'Pérez', 'telefono': '987654321'},
            {'username': 'cliente2', 'email': 'cliente2@mail.com', 'first_name': 'María', 'last_name': 'García', 'telefono': '987654322'},
            {'username': 'cliente3', 'email': 'cliente3@mail.com', 'first_name': 'Carlos', 'last_name': 'López', 'telefono': '987654323'},
        ]
        
        clientes = []
        for data in clientes_data:
            if not Usuario.objects.filter(username=data['username']).exists():
                cliente = Usuario.objects.create_user(
                    username=data['username'],
                    email=data['email'],
                    password='cliente123',
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    telefono=data['telefono'],
                    direccion=f'Calle Principal 123, Huacho',
                    rol='CLIENTE'
                )
                clientes.append(cliente)
                self.stdout.write(self.style.SUCCESS(f'✓ Cliente creado: {data["username"]}/cliente123'))
        
        # Crear categorías
        categorias_data = [
            {'nombre': 'Miel Natural', 'descripcion': 'Miel pura 100% natural'},
            {'nombre': 'Polen', 'descripcion': 'Polen de abejas natural'},
            {'nombre': 'Propóleo', 'descripcion': 'Propóleo natural de abejas'},
            {'nombre': 'Jalea Real', 'descripcion': 'Jalea real fresca'},
            {'nombre': 'Cera de Abeja', 'descripcion': 'Cera natural de abeja'},
        ]
        
        categorias = {}
        for data in categorias_data:
            cat, created = Categoria.objects.get_or_create(
                nombre=data['nombre'],
                defaults={'descripcion': data['descripcion']}
            )
            categorias[data['nombre']] = cat
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Categoría creada: {data["nombre"]}'))
        
        # Crear productos
        productos_data = [
            {
                'nombre': 'Miel Pura de Abeja 500g',
                'descripcion': 'Miel 100% pura y natural extraída de colmenas locales. Rica en antioxidantes y propiedades antibacterianas.',
                'precio': Decimal('25.00'),
                'stock': 50,
                'categoria': categorias['Miel Natural']
            },
            {
                'nombre': 'Miel Pura de Abeja 1kg',
                'descripcion': 'Miel natural de alta calidad en presentación de 1 kilogramo. Ideal para toda la familia.',
                'precio': Decimal('45.00'),
                'stock': 35,
                'categoria': categorias['Miel Natural']
            },
            {
                'nombre': 'Polen Natural 250g',
                'descripcion': 'Polen recolectado por abejas, rico en proteínas, vitaminas y minerales. Excelente suplemento nutricional.',
                'precio': Decimal('30.00'),
                'stock': 25,
                'categoria': categorias['Polen']
            },
            {
                'nombre': 'Propóleo en Gotas 30ml',
                'descripcion': 'Extracto de propóleo natural. Fortalece el sistema inmunológico y tiene propiedades antisépticas.',
                'precio': Decimal('35.00'),
                'stock': 40,
                'categoria': categorias['Propóleo']
            },
            {
                'nombre': 'Jalea Real Fresca 50g',
                'descripcion': 'Jalea real pura y fresca. Energizante natural y estimulante del sistema inmunológico.',
                'precio': Decimal('80.00'),
                'stock': 15,
                'categoria': categorias['Jalea Real']
            },
            {
                'nombre': 'Cera de Abeja Natural 500g',
                'descripcion': 'Cera de abeja pura para uso cosmético y artesanal. 100% natural.',
                'precio': Decimal('28.00'),
                'stock': 20,
                'categoria': categorias['Cera de Abeja']
            },
            {
                'nombre': 'Miel con Polen 500g',
                'descripcion': 'Combinación perfecta de miel pura con polen natural. Doble beneficio nutricional.',
                'precio': Decimal('32.00'),
                'stock': 30,
                'categoria': categorias['Miel Natural']
            },
            {
                'nombre': 'Set Salud Completo',
                'descripcion': 'Set que incluye miel 500g, polen 250g y propóleo en gotas. Pack completo para tu salud.',
                'precio': Decimal('85.00'),
                'stock': 10,
                'categoria': categorias['Miel Natural']
            },
        ]
        
        productos = []
        for data in productos_data:
            prod, created = Producto.objects.get_or_create(
                nombre=data['nombre'],
                defaults={
                    'descripcion': data['descripcion'],
                    'precio': data['precio'],
                    'stock': data['stock'],
                    'categoria': data['categoria'],
                    'activo': True
                }
            )
            productos.append(prod)
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Producto creado: {data["nombre"]}'))
        
        # Crear pedidos de prueba
        if clientes:
            estados = ['PENDIENTE', 'PROCESANDO', 'ENVIADO', 'ENTREGADO']
            for i in range(10):
                cliente = random.choice(clientes)
                pedido = Pedido.objects.create(
                    cliente=cliente,
                    estado=random.choice(estados),
                    direccion_envio=cliente.direccion,
                    notas=f'Pedido de prueba #{i+1}'
                )
                
                # Agregar productos al pedido
                num_productos = random.randint(1, 3)
                for _ in range(num_productos):
                    producto = random.choice(productos)
                    cantidad = random.randint(1, 3)
                    DetallePedido.objects.create(
                        pedido=pedido,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=producto.precio
                    )
                
                pedido.calcular_total()
                self.stdout.write(self.style.SUCCESS(f'✓ Pedido creado: #{pedido.id}'))
        
        self.stdout.write(self.style.SUCCESS('\n¡Datos de prueba cargados exitosamente!'))
        self.stdout.write(self.style.WARNING('\nCredenciales de acceso:'))
        self.stdout.write(self.style.WARNING('Admin: admin / admin123'))
        self.stdout.write(self.style.WARNING('Clientes: cliente1, cliente2, cliente3 / cliente123'))