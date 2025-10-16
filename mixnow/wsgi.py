import os
from django.core.wsgi import get_wsgi_application

# Configura el módulo de settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mixnow.settings')

# Crear la aplicación WSGI
application = get_wsgi_application()
