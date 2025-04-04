from django.contrib import admin
from .models import Letting, Address


admin.site.register(Letting)  # Registers Letting model to manage lettings in the admin interface
admin.site.register(Address)  # Registers Address model to manage addresses in the admin interface
