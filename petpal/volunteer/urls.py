from django.urls import path
from . import views
urlpatterns = [
    # path('', views.volunteerHome, name='volunteerHome'),
    path('volunteerSignup/', views.volunteerSignup, name='volunteerSignup'),
    path('volunteerLogin/', views.volunteerLogin, name='volunteerLogin'),
    path('volunteerHome/', views.volunteerHome, name='volunteerHome'),
    path('volunteerAppointments/', views.volunteerAppointments, name='volunteerAppointments'),
    path('volunteerPets/', views.volunteerPets, name='volunteerPets'),
    path('volunteerNotification/', views.volunteerNotification, name='volunteerNotification'),
]