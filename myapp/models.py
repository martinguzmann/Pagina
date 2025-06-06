from django.db import models
from django.conf import settings
  
class Registro(models.Model):
    
    id_registro = models.AutoField(primary_key=True)
    usuario = models.CharField(max_length=50, unique=True) # Hacemos el usuario único
    email = models.EmailField()
    telefono = models.CharField(max_length=20) # Ajusta max_length según necesites
    contraseña = models.CharField(max_length=128) # Guarda la contraseña tal cual se recibe
    fecha_registro = models.DateTimeField(auto_now_add=True) # Opcional: guardar cuándo se registró

    def __str__(self):
        return self.usuario    

class Camilla(models.Model):
    id_camilla = models.AutoField(primary_key=True)
    estado = models.CharField(max_length=20)
    
    def __int__ (self):
        return self.id_camilla
    
class Paciente(models.Model):
    id_paciente = models.AutoField(primary_key=True)
    nombre_pac = models.CharField(max_length=40)
    apellido_pac = models.CharField(max_length=40)
    rut = models.CharField(max_length=12, unique=True) # RUT único
    email = models.EmailField() 
    telefono = models.CharField(max_length=15)
    fecha_nacimiento = models.DateField()
    sexo = models.CharField(max_length=10) # 'M' o 'F'
    motivo_consulta = models.CharField(max_length=200) # Motivo de ingreso
    fecha_registro = models.DateTimeField(auto_now_add=True) # Opcional: guardar cuándo se registró    
    fecha_salida = models.DateField(null=True, blank=True) # Fecha de salida del paciente
    id_camilla = models.ForeignKey(Camilla, on_delete=models.CASCADE, null=True, blank=True) # Relación con la tabla camilla
    id_registro = models.ForeignKey(Registro, on_delete=models.CASCADE, null=True, blank=True) # Relación con la tabla registro
    
    def __str__(self):
        return self.nombre_pac + " " + self.apellido_pac
    
class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    monto = models.DecimalField(max_digits=10, decimal_places=2) 
    descripcion = models.CharField(max_length=200)
    imagen = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.nombre

class TransaccionPaypal(models.Model):
    payer_id = models.CharField(max_length=250)
    payment_date = models.DateTimeField()
    payment_status = models.CharField(max_length=250)
    quantity = models.IntegerField()
    invoice = models.CharField(max_length=250)
    first_name = models.CharField(max_length=250)
    payer_status = models.CharField(max_length=250)
    payer_email = models.CharField(max_length=250)  
    txn_id = models.CharField(max_length=250)
    receiver_id = models.CharField(max_length=250)
    payment_gross = models.FloatField()
    custom = models.CharField(max_length=250)

    def __str__(self):
        return self.custom


#------------------------------------------------------------------------------------------------------------------------

class Pedido(models.Model):
   
    registro_usuario = models.ForeignKey(Registro, on_delete=models.SET_NULL, null=True, blank=True, related_name="pedidos")
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True) 
    paypal_order_id = models.CharField(max_length=100, unique=True) 
    paypal_capture_id = models.CharField(max_length=100, unique=True, null=True, blank=True) # El ID de la captura (transacción)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    moneda = models.CharField(max_length=10, default="USD") 
    ESTADOS_PEDIDO = [
        ('PENDIENTE', 'Pendiente'),
        ('COMPLETADO', 'Completado'),
        ('FALLIDO', 'Fallido'),
        ('REEMBOLSADO', 'Reembolsado'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS_PEDIDO, default='PENDIENTE')

    payer_email = models.EmailField(blank=True, null=True)
    payer_id_paypal = models.CharField(max_length=100, blank=True, null=True) # El ID del pagador en PayPal
    payer_nombre = models.CharField(max_length=200, blank=True, null=True)

    fecha_creacion_pedido = models.DateTimeField(auto_now_add=True) # Cuando se creó el registro en nuestra BD
    fecha_actualizacion = models.DateTimeField(auto_now=True) # Cuando se actualizó por última vez

    def __str__(self):
        user_display = self.registro_usuario.usuario if self.registro_usuario else "Invitado"
        return f"Pedido {self.id} por {user_display} - {self.producto.nombre if self.producto else 'Producto no disponible'}"

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-fecha_creacion_pedido']

