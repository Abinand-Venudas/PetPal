from django.urls import path
from . import views

app_name = "petadmin"

urlpatterns = [

    # ================= AUTH =================
    path("", views.homeAdmin, name="homeAdmin"),
    path("login/", views.loginAdmin, name="loginAdmin"),
    path("logout/", views.logoutAdmin, name="logoutAdmin"),

    # ================= DASHBOARD =================
    path("home/", views.homeAdmin, name="homeAdmin"),

    # ================= DOCTORS =================
    path("doctor/", views.doctorAdmin, name="doctorAdmin"),
    path("doctor/delete/<int:id>/", views.deleteDoctor, name="deleteDoctor"),
    path("doctor/toggle/<int:id>/", views.toggleDoctorAvailability, name="toggleDoctorAvailability"),
    path("doctor/details/<int:id>/", views.doctorDetailsAdmin, name="doctorDetailsAdmin"),

    # ================= VOLUNTEERS =================
    path("volunteer/", views.volunteerAdmin, name="volunteerAdmin"),
    path("volunteer/toggle/<int:id>/", views.toggleVolunteerAvailability, name="toggleVolunteerAvailability"),

    # ================= USERS =================
    path("users/", views.userAdmin, name="userAdmin"),
    path("user/details/<int:id>/", views.userDetailsAdmin, name="userDetailsAdmin"),
    path("user/toggle/<int:id>/", views.toggleUserStatus, name="toggleUserStatus"),
    path("user/delete/<int:id>/", views.deleteUser, name="deleteUser"),

    # ================= ADOPTION PETS =================
    path("adoption/pets/", views.adoptionPetsAdmin, name="adoptionPetsAdmin"),
    path("adoption/pets/add/", views.addPetAdmin, name="addPetAdmin"),
    path("adoption/pets/edit/<int:id>/", views.editPetAdmin, name="editPetAdmin"),
    path("adoption/pets/delete/<int:id>/", views.deletePetAdmin, name="deletePetAdmin"),

    # ================= CONSULTATIONS =================
    path("consultations/", views.consultationAdmin, name="consultationAdmin"),

    # ================= ADOPTIONS =================
    path("adoptions/", views.adminAdoptions, name="adminAdoptions"),
    path("adoptions/view/<int:id>/", views.adminAdoptionView, name="adminAdoptionView"),
    path("adoptions/update/<int:id>/<str:status>/", views.update_adoption_status, name="update_adoption_status"),

    # ================= GROOMING BOOKINGS =================
    path("grooming/bookings/", views.adminGroomingBookings, name="adminGroomingBookings"),
    path("grooming/assign/<int:booking_id>/", views.assignGroomingVolunteer, name="assignGroomingVolunteer"),
    path("grooming/status/<int:booking_id>/<str:status>/", views.updateGroomingStatus, name="updateGroomingStatus"),

    # ================= SERVICES (NEW CLEAN SYSTEM) =================

    # Grooming services
    path("services/grooming/", views.groomingServicesAdmin, name="groomingServicesAdmin"),
    path("services/grooming/add/", views.addGroomingServiceAdmin, name="addGroomingServiceAdmin"),
    path("services/grooming/edit/<int:id>/",views.editGroomingServiceAdmin, name="editGroomingServiceAdmin"),
    path("services/grooming/delete/<int:id>/",views.deleteGroomingServiceAdmin,name="deleteGroomingServiceAdmin"),

    # Daycare plans
    path("services/daycare/", views.daycarePlansAdmin, name="daycarePlansAdmin"),
    path("services/daycare/add/", views.addDaycarePlanAdmin, name="addDaycarePlanAdmin"),
    path("services/daycare/edit/<int:id>/",views.editDaycarePlanAdmin,name="editDaycarePlanAdmin"),
    path("services/daycare/delete/<int:id>/",views.deleteDaycarePlanAdmin,name="deleteDaycarePlanAdmin"),
    path(
    "services/daycare/toggle/<int:id>/",
    views.toggleDaycarePlanStatusAdmin,
    name="toggleDaycarePlanStatusAdmin"
),

]
