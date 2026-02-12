from django.urls import path
from . import views

app_name = 'volunteer'

urlpatterns = [
    path('volunteerSignup/', views.volunteerSignup, name='volunteerSignup'),
    path('volunteerLogin/', views.volunteerLogin, name='volunteerLogin'),
    path('volunteerHome/', views.volunteerHome, name='volunteerHome'),

    path('volunteerAppointments/', views.volunteerAppointments, name='volunteerAppointments'),
    path('volunteerPets/', views.volunteerPets, name='volunteerPets'),
    path('volunteerNotification/', views.volunteerNotification, name='volunteerNotification'),

    path('checkin/', views.volunteerCheckIn, name='volunteerCheckIn'),
    path('checkout/', views.volunteerCheckOut, name='volunteerCheckOut'),

    # ✅ NEW
    path('attendance/', views.volunteerAttendanceHistory, name='volunteerAttendance'),
    path("tasks/", views.volunteerTasks, name="volunteerTasks"),
    path("notification/read/<int:id>/", views.mark_notification_read, name="mark_notification_read"),

    path('profile/', views.volunteerProfile, name='volunteerProfile'),
    path('change-password/', views.volunteerChangePassword, name='volunteerChangePassword'),
    path('logout/', views.volunteerLogout, name='volunteerLogout'),
    path("apply/", views.volunteerApply, name="apply"),
    path("apply/success/", views.volunteerApplySuccess, name="apply_success"),
    path("notifications/count/",views.notification_count_api,name="notification_count_api"),
    path("appointments/complete/<int:booking_id>/", views.markAppointmentCompleted, name="markAppointmentCompleted"),

    # volunteer/urls.py
    path("verify-code/", views.verify_code, name="verify_code"),

]
