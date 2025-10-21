from django import forms
from .models import Cliente, Item

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['Rut', 'cliente', 'telefono', 'obra', 'persona_contacto']
        widgets = {
            'Rut': forms.TextInput(attrs={'class': 'form-control'}),
            'cliente': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'obra': forms.TextInput(attrs={'class': 'form-control'}),
            'persona_contacto': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['cantidad_m3', 'descripcion' , 'moneda', 'precio_unitario']
        labels = {
            'cantidad_m3': 'Cantidad (m³)',
        }
        widgets = {
            'cantidad_m3': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Arena fina'}), 
            'moneda': forms.Select(attrs={'class': 'form-control'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }


