from django import forms

from petpal.petapp.models import Service
from .models import GroomingService, DaycarePlan

class GroomingServiceForm(forms.ModelForm):
    class Meta:
        model = GroomingService
        fields = ["name", "price", "icon", "is_active"]

class DaycarePlanForm(forms.ModelForm):
    class Meta:
        model = DaycarePlan
        fields = ["name", "price", "duration_days", "is_active"]

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ["name", "price", "duration", "icon", "description", "service_type"]