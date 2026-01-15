from django.urls import path
from . import views

app_name = "petapp"

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.userLogin, name="login"),
    path("register/", views.userReg, name="register"),
    path("logout/", views.userLogout, name="logout"),

    # Profile
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("profile/change-password/", views.change_password, name="change_password"),
    path("my-bookings/", views.my_bookings, name="my_bookings"),
    path("booking/pdf/<int:booking_id>/", views.download_booking_pdf, name="download_booking_pdf"),

    # Pages
    path("grooming/", views.grooming, name="grooming"),
    path("daycare/", views.daycare, name="daycare"),
    path("consultation/", views.consultation, name="consultation"),
    path("adoption/adoptionlist/", views.adoptionlist, name="adoptionlist"),

    # Pet
    path("pet/<int:pet_id>/", views.petDetails, name="petDetails"),
    path("adopt/<int:pet_id>/", views.adoptPet, name="adoptPet"),

    # Success
    path("consultation/success/<int:id>/", views.consultationSuccess, name="consultationSuccess"),
    path("grooming/success/", views.groomSuccess, name="groomsuccess"),
    path("adoption/success/<int:id>/", views.adoptionSuccess, name="adoptionSuccess"),
    path("confirmbook/", views.confirmbook, name="confirmbook"),
    path("daycareSuccess/<int:id>/", views.daycareSuccess, name="daycareSuccess"),
    path("api/daycare-booked-slots/", views.get_daycare_booked_slots, name="get_daycare_booked_slots"),

    # API
    path("api/booked-slots/", views.get_booked_slots, name="get_booked_slots"),
    path("api/lock-slot/", views.lock_slot, name="lock_slot"),
    path("api/release-slot/", views.release_slot, name="release_slot"),
]
