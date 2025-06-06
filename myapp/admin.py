from django.contrib import admin
from .models import Registro, Camilla, Paciente, TransaccionPaypal, Producto, Pedido
# Register your models here.
admin.site.register(Registro)
admin.site.register(Camilla)
admin.site.register(Paciente)
admin.site.register(Producto)
admin.site.register(TransaccionPaypal)
admin.site.register(Pedido)