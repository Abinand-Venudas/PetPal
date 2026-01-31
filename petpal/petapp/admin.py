from django.contrib import admin
from .models import *

admin.site.register(user_registration)
admin.site.register(Pet)
admin.site.register(AdoptionRequest)
admin.site.register(Consultation)
admin.site.register(SlotLock)
admin.site.register(DaycareSlotLock)

admin.site.register(DaycareBooking)
# admin.site.register(Service)
admin.site.register(GroomingSlotLock)
admin.site.register(GroomingBooking)
