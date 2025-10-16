from django.urls import reverse, reverse_lazy
from django.views.generic.list import ListView 
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.detail import DetailView
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import ClienteForm, ItemForm
from .models import Cliente, Item, Cotizacion
from django.views.generic.edit import FormMixin
from django.http import HttpResponseRedirect
from django.template.loader import get_template


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


@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class Detalle_Clientes(LoginRequiredMixin, UserPassesTestMixin, FormMixin, DetailView):
    model = Cliente
    template_name = "clientes/detalle_cliente.html"
    context_object_name = 'cliente'
    form_class = ItemForm

    def test_func(self):
        return self.request.user.is_superuser

    def get_success_url(self):
        return reverse('detalle_cliente', kwargs={'pk': self.object.pk})

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        opcion_destino = request.POST.get('opcion_destino')

        if form.is_valid():
            # Crear una nueva cotización para este cliente
            empresa = opcion_destino.capitalize()
            cotizacion = Cotizacion.objects.create(cliente=self.object, empresa=empresa)

            # Guardar el ítem asociado a la cotización
            item = form.save(commit=False)
            item.cotizacion = cotizacion
            item.save()

            # Redirigir según la opción seleccionada (ahora con el ID de la cotización)
            if opcion_destino == "aridos":
                return HttpResponseRedirect(reverse('vista_aridos', kwargs={'cotizacion_id': cotizacion.id}))
            elif opcion_destino == "valentino":
                return HttpResponseRedirect(reverse('vista_valentino', kwargs={'cotizacion_id': cotizacion.id}))
            elif opcion_destino == "inverland":
                return HttpResponseRedirect(reverse('vista_inverland', kwargs={'cotizacion_id': cotizacion.id}))
            elif opcion_destino == "mixnow":
                return HttpResponseRedirect(reverse('vista_mixnow', kwargs={'cotizacion_id': cotizacion.id}))

        return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()

        # Tomar solo los ítems de la última cotización
        last_cotizacion = self.object.cotizacion_set.last()
        context['cotizacion'] = last_cotizacion
        context['items'] = last_cotizacion.items.all() if last_cotizacion else []
        return context



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
import weasyprint

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
    weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf(response)
    return response


#INSTRUCCIONES 
@user_passes_test(lambda u: u.is_superuser)
def instrucciones(request):
    return render(request, 'clientes/instrucciones.html')

