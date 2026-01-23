from django.db import models
from django.utils import timezone


class volunteer_registration(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # hashed
    proof = models.FileField(upload_to='volunteer_docs', default=True)
    phone = models.CharField(max_length=15, default='True')
    skills = models.CharField(max_length=30, default='True')
    address = models.TextField(default='True')
    is_available = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class VolunteerAttendance(models.Model):
    volunteer = models.ForeignKey(
        volunteer_registration,
        on_delete=models.CASCADE
    )
    check_in = models.DateTimeField(default=timezone.now)
    check_out = models.DateTimeField(null=True, blank=True)

    def worked_hours(self):
        if self.check_out:
            delta = self.check_out - self.check_in
            return round(delta.total_seconds() / 3600, 2)
        return 0

    def __str__(self):
        return f"{self.volunteer.name} | {self.check_in}"
