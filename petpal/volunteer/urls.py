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
]
