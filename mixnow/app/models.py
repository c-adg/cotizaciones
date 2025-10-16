from django.db import models
from django.core.validators import RegexValidator

# VALIDADOR DE TELEFONO
telefono_validator = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',  # Ejemplo: permite +56912345678
    message="El número de teléfono debe tener formato: +569XXXXXXXX o 9 dígitos"
)

class Cliente(models.Model):
    Rut = models.CharField(max_length=12)
    cliente = models.CharField(max_length=100)
    telefono = models.CharField(validators=[telefono_validator], max_length=12, blank=True, null=True, default='')
    obra = models.CharField(max_length=50, blank=True, null=True, default='')
    persona_contacto = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.Rut} - {self.cliente}"


class Cotizacion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    empresa = models.CharField(max_length=50)  # Ej: 'MixNow', 'Aridos'
    fecha = models.DateField(auto_now_add=True)
    numero_cotizacion = models.IntegerField(editable=False)

    def save(self, *args, **kwargs):
        if not self.pk:
            # Buscar la última cotización solo para esta empresa
            ultima = Cotizacion.objects.filter(empresa=self.empresa).order_by('-numero_cotizacion').first()
            if ultima:
                self.numero_cotizacion = ultima.numero_cotizacion + 1
            else:
                self.numero_cotizacion = 3000  # Cada empresa empieza desde 3000
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Cotización {self.numero_cotizacion} - {self.cliente} ({self.empresa})"



class Item(models.Model):
    cotizacion = models.ForeignKey(Cotizacion, on_delete=models.CASCADE, related_name='items')
    cantidad_m3 = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.CharField(max_length=100, blank=False, null=False)
    valido_hasta = models.DateField()

    MONEDAS = (
        ('CLP', 'CLP'),
        ('UF', 'UF'),
    )
    moneda = models.CharField(max_length=3, choices=MONEDAS, default='CLP')

    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    IVA = 0.19  # 19%

    def subtotal(self):
        return float(self.cantidad_m3) * float(self.precio_unitario)

    def iva(self):
        return self.subtotal() * self.IVA

    def total(self):
        return self.subtotal() + self.iva()

    def __str__(self):
        return f"{self.descripcion} ({self.cotizacion.cliente})"
