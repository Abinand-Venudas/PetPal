from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.userLogin, name='login'),       
    path('register/', views.userReg, name='register'),     
    path('grooming/', views.grooming, name='grooming'),
    path('daycare/', views.daycare, name='daycare'),
    path('consultation/', views.consultation, name='consultation'),
    path('login/userForm/', views.userForm, name='userForm'),
    path('adoption/adoptionlist/', views.adoptionlist, name='adoptionlist'),
    path('userHome/', views.userHome, name='userHome'),
]
