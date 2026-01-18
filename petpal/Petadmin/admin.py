from django.contrib import admin
from petapp.models import Service   # ✅ ADD THIS LINE

admin.site.register(Service)
