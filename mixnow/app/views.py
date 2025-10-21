from django.urls import reverse, reverse_lazy
from django.views.generic.list import ListView 
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.detail import DetailView
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import ClienteForm, ItemForm
from .models import Cliente, Item, Cotizacion
from django.http import HttpResponseRedirect
from django.contrib import messages

@user_passes_test(lambda u: u.is_superuser)
def inicio(request):
    return render(request, 'clientes/inicio.html')


@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class Listar_Clientes(LoginRequiredMixin, UserPassesTestMixin, ListView):
    def test_func(self):
        return self.request.user.is_superuser
    model = Cliente
    template_name = "clientes/listar_clientes.html"
    context_object_name = 'clientes'


@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class Crear_Cliente(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    def test_func(self):
        return self.request.user.is_superuser
    model = Cliente
    form_class = ClienteForm
    template_name = "clientes/crear_cliente.html"
    success_url = reverse_lazy('listar_clientes')


@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class Editar_Cliente(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    def test_func(self):
        return self.request.user.is_superuser
    model = Cliente
    form_class = ClienteForm
    template_name = "clientes/editar_cliente.html"
    success_url = reverse_lazy('listar_clientes')


@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class Eliminar_Cliente(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    def test_func(self):
        return self.request.user.is_superuser
    model = Cliente
    template_name = "clientes/eliminar_cliente.html"
    success_url = reverse_lazy('listar_clientes')


# ==========================
# VISTA DETALLE CLIENTE - AGREGAR ITEMS
# ==========================
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class Detalle_Clientes(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Cliente
    template_name = "clientes/detalle_cliente.html"
    context_object_name = 'cliente'
    form_class = ItemForm

    def test_func(self):
        # Permite solo superusuarios
        return self.request.user.is_superuser

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        accion = request.POST.get('accion')

        # Inicializamos la sesión si no existe
        if 'items_temporales' not in request.session:
            request.session['items_temporales'] = []

        # -----------------------------
        # Agregar item temporal
        # -----------------------------
        if accion == 'agregar_item':
            form = ItemForm(request.POST)
            if form.is_valid():
                item_data = {
                    'cantidad_m3': float(form.cleaned_data['cantidad_m3']),
                    'descripcion': form.cleaned_data['descripcion'],
                    'moneda': form.cleaned_data['moneda'],
                    'precio_unitario': float(form.cleaned_data['precio_unitario']),
                }
                # Guardamos el item en la sesión
                request.session['items_temporales'].append(item_data)
                request.session.modified = True
            return redirect('detalle_cliente', pk=self.object.pk)

        # -----------------------------
        # Eliminar item temporal
        # -----------------------------
        elif accion == 'eliminar_item':
            index = int(request.POST.get('item_index'))
            if 0 <= index < len(request.session['items_temporales']):
                request.session['items_temporales'].pop(index)
                request.session.modified = True
            return redirect('detalle_cliente', pk=self.object.pk)

        # -----------------------------
        # Crear cotización
        # -----------------------------
        elif accion == 'crear_cotizacion':
            # Llamamos a la función que maneja la creación de la cotización
            return self.crear_cotizacion(request)

        # Si no es ninguna acción, redirigimos al detalle
        return redirect('detalle_cliente', pk=self.object.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pasamos el formulario y los items temporales a la plantilla
        context['form'] = ItemForm()
        context['items_temporales'] = self.request.session.get('items_temporales', [])
        return context

    # ==========================
    # FUNCION PARA CREAR COTIZACION
    # ==========================
    def crear_cotizacion(self, request):
        """
        Método para crear una cotización a partir de los ítems temporales almacenados en la sesión.
        Se ejecuta cuando el usuario presiona el botón 'Crear Cotización'.
        """

        # Obtenemos los datos enviados por POST desde el formulario de crear cotización
        opcion_destino = request.POST.get('opcion_destino')  # Empresa seleccionada
        valido_hasta = request.POST.get('valido_hasta')      # Fecha de validez

        # Validamos que haya al menos un ítem agregado
        if not request.session.get('items_temporales'):
            messages.error(request, "Debes agregar al menos un ítem antes de crear la cotización.")
            return redirect('detalle_cliente', pk=self.object.pk)

        # Creamos la cotización en la base de datos
        cotizacion = Cotizacion.objects.create(
            cliente=self.object,
            empresa=opcion_destino.capitalize(),
            valido_hasta=valido_hasta
        )

        # Creamos los ítems asociados a la cotización
        for i in request.session['items_temporales']:
            Item.objects.create(
                cotizacion=cotizacion,
                cantidad_m3=i['cantidad_m3'],
                descripcion=i['descripcion'],
                moneda=i['moneda'],
                precio_unitario=i['precio_unitario']
            )

        # Limpiamos los ítems de la sesión ya que fueron creados en DB
        request.session['items_temporales'] = []
        request.session.modified = True

        # Redirigimos según la empresa seleccionada
        rutas = {
            "aridos": 'vista_aridos',
            "valentino": 'vista_valentino',
            "inverland": 'vista_inverland',
            "mixnow": 'vista_mixnow'
        }
        return HttpResponseRedirect(reverse(rutas[opcion_destino], kwargs={'cotizacion_id': cotizacion.id}))




# PLANTILLAS DE LAS 4 EMPRESAS DIFERENTES

# Aridos
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class CotizacionAridosView(DetailView):
    model = Cotizacion
    template_name = "clientes/aridos.html"
    context_object_name = "cotizacion"

    def get_object(self):
        cotizacion_id = self.kwargs.get('cotizacion_id')
        return Cotizacion.objects.get(id=cotizacion_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.all()
        context['cliente'] = self.object.cliente
        return context


# Valentino
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class CotizacionValentinoView(DetailView):
    model = Cotizacion
    template_name = "clientes/valentino.html"
    context_object_name = "cotizacion"

    def get_object(self):
        cotizacion_id = self.kwargs.get('cotizacion_id')
        return Cotizacion.objects.get(id=cotizacion_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.all()
        context['cliente'] = self.object.cliente
        return context


# Inverland
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class CotizacionInverlandView(DetailView):
    model = Cotizacion
    template_name = "clientes/inverland.html"
    context_object_name = "cotizacion"

    def get_object(self):
        cotizacion_id = self.kwargs.get('cotizacion_id')
        return Cotizacion.objects.get(id=cotizacion_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.all()
        context['cliente'] = self.object.cliente
        return context


# MixNow
class CotizacionMixNowView(DetailView):
    model = Cotizacion
    template_name = "clientes/mixnow.html"
    context_object_name = "cotizacion"

    def get_object(self):
        cotizacion_id = self.kwargs.get('cotizacion_id')
        return Cotizacion.objects.get(id=cotizacion_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.all()
        context['cliente'] = self.object.cliente
        return context



from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML, CSS


def descargar_pdf(request, cotizacion_id, plantilla):
    cotizacion = Cotizacion.objects.get(id=cotizacion_id)
    items = cotizacion.items.all()
    cliente = cotizacion.cliente

    html_string = render_to_string(f'clientes/{plantilla}.html', {
        'cliente': cliente,
        'cotizacion': cotizacion,
        'items': items
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="cotizacion_{cotizacion.id}.pdf"'

    # AQUI SE APLICA EL TAMAÑO A4 AL PDF PARA OCUPAR MAS ESPACIO DE LA HOJA 
    HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf(
        response,
        stylesheets=[
            CSS(string='''
                @page {
                    size: A4;
                    margin-top: -1.3cm; 
                    margin-left: 0cm;
                    margin-right: 0cm;
                    margin-bottom: 0cm;
                }
            ''')
        ]
    )

    return response


#INSTRUCCIONES 
@user_passes_test(lambda u: u.is_superuser)
def instrucciones(request):
    return render(request, 'clientes/instrucciones.html')

