from django.urls import path
from . import views

app_name = "petadmin"

urlpatterns = [

    # ================= AUTH =================
    path('', views.homeAdmin, name='homeAdmin'),
    path('login/', views.loginAdmin, name='loginAdmin'),
    path('logout/', views.logoutAdmin, name='logoutAdmin'),

    # ================= DASHBOARD =================
    path('home/', views.homeAdmin, name='homeAdmin'),

    # ================= DOCTORS =================
    path('doctor/', views.doctorAdmin, name='doctorAdmin'),
    path('doctor/delete/<int:id>/', views.deleteDoctor, name='deleteDoctor'),
    path('doctor/toggle/<int:id>/', views.toggleDoctorAvailability, name='toggleDoctorAvailability'),
    path('doctor/details/<int:id>/', views.doctorDetailsAdmin, name='doctorDetailsAdmin'),

    # ================= VOLUNTEERS =================
    path('volunteer/', views.volunteerAdmin, name='volunteerAdmin'),
    path('volunteer/toggle/<int:id>/', views.toggleVolunteerAvailability, name='toggleVolunteerAvailability'),

    # ================= USERS =================
    path('users/', views.userAdmin, name='userAdmin'),
    path('user/details/<int:id>/', views.userDetailsAdmin, name='userDetailsAdmin'),
    path('user/toggle/<int:id>/', views.toggleUserStatus, name='toggleUserStatus'),
    path('user/delete/<int:id>/', views.deleteUser, name='deleteUser'),

    # ================= ADOPTION PETS =================
    path('adoption/pets/', views.adoptionPetsAdmin, name='adoptionPetsAdmin'),
    path('adoption/pets/add/', views.addPetAdmin, name='addPetAdmin'),
    path('adoption/pets/edit/<int:id>/', views.editPetAdmin, name='editPetAdmin'),
    path('adoption/pets/delete/<int:id>/', views.deletePetAdmin, name='deletePetAdmin'),

    # ================= CONSULTATIONS =================
    path('consultations/', views.consultationAdmin, name='consultationAdmin'),

    # ================= ADOPTION REQUESTS =================
    path('adoptions/', views.adminAdoptions, name='adminAdoptions'),
    path('adoption/view/<int:id>/', views.adminAdoptionView, name='adminAdoptionView'),
    path('adoption/update/<int:id>/<str:status>/', views.update_adoption_status, name='update_adoption_status'),

   # ================= SERVICES =================
path('services/', views.serviceAdmin, name='serviceAdmin'),
path('services/add/', views.addServiceAdmin, name='addServiceAdmin'),
path('services/edit/<int:id>/', views.editServiceAdmin, name='editServiceAdmin'),
path('services/delete/<int:id>/', views.deleteServiceAdmin, name='deleteServiceAdmin'),

    ]