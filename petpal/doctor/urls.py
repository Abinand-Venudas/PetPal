from django.urls import path
from . import views

app_name = 'doctor'

urlpatterns = [
    path('doctorLogin/', views.doctorLogin, name='doctorLogin'),
    path('doctorSignup/', views.doctorSignup, name='doctorSignup'),
    path('doctorHome/', views.doctorHome, name='doctorHome'),
    path('appointment/<int:appointment_id>/<str:status>/', views.updateAppointment, name='updateAppointment'),
     path('doctoractive/', views.doctoractive, name='doctoractive'),
    path('doctorcheckout/', views.doctorcheckout, name='doctorcheckout'),
]
