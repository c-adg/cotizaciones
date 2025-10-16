from django.urls import path
from app import views
from django.contrib import admin
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Inicio y cierre de sesión
    path('', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # CRUD de clientes
    path('inicio/', views.inicio, name='inicio'),
    path('clientes/', views.Listar_Clientes.as_view(), name='listar_clientes'),
    path('cliente/crear/', views.Crear_Cliente.as_view(), name='crear_cliente'),
    path('cliente/editar/<int:pk>/', views.Editar_Cliente.as_view(), name='editar_cliente'),
    path('cliente/eliminar/<int:pk>/', views.Eliminar_Cliente.as_view(), name='eliminar_cliente'),
    path('cliente/detalle/<int:pk>/', views.Detalle_Clientes.as_view(), name='detalle_cliente'),

    path('clientes/aridos/<int:cotizacion_id>/', views.CotizacionAridosView.as_view(), name='vista_aridos'),
    path('clientes/valentino/<int:cotizacion_id>/', views.CotizacionValentinoView.as_view(), name='vista_valentino'),
    path('clientes/inverland/<int:cotizacion_id>/', views.CotizacionInverlandView.as_view(), name='vista_inverland'),
    path('clientes/mixnow/<int:cotizacion_id>/', views.CotizacionMixNowView.as_view(), name='vista_mixnow'),


    path('pdf/<int:cotizacion_id>/<str:plantilla>/', views.descargar_pdf, name='generar_pdf'),
    path('instrucciones/', views.instrucciones, name = 'instrucciones'),

]
