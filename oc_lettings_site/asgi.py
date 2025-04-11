import os
from django.core.asgi import get_asgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oc_lettings_site.settings')
application = get_asgi_application()
"""
Sets the default Django settings module for
the 'oc_lettings_site' project and exposes
the ASGI application callable as 'application'.
"""
