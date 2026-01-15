from django.contrib import admin
from .models import user_registration, Pet

admin.site.register(user_registration)
admin.site.register(Pet)
