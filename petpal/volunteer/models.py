from datetime import timedelta
import uuid
from django.db import models
from django.utils import timezone


class volunteer_registration(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    proof = models.FileField(upload_to='volunteer_docs', null=True, blank=True)

    phone = models.CharField(max_length=15)
    skills = models.CharField(max_length=30)
    address = models.TextField()

    is_active = models.BooleanField(default=True)
    is_available = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class VolunteerAttendance(models.Model):
    volunteer = models.ForeignKey(volunteer_registration, on_delete=models.CASCADE)
    check_in = models.DateTimeField(default=timezone.now)
    check_out = models.DateTimeField(null=True, blank=True)

    def worked_hours(self):
        if self.check_out:
            delta = self.check_out - self.check_in
            return round(delta.total_seconds() / 3600, 2)
        return 0


class VolunteerTask(models.Model):
    volunteer = models.ForeignKey(volunteer_registration, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    task_time = models.DateTimeField()
    status = models.CharField(
        max_length=30,
        choices=[('upcoming', 'Upcoming'), ('completed', 'Completed')],
        default='upcoming'
    )


class VolunteerPet(models.Model):
    volunteer = models.ForeignKey(volunteer_registration, on_delete=models.CASCADE)
    pet_name = models.CharField(max_length=100)
    species = models.CharField(max_length=50)
    assigned_on = models.DateField(auto_now_add=True)


class VolunteerNotification(models.Model):
    volunteer = models.ForeignKey(
        volunteer_registration,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=300, blank=True, null=True)

    def __str__(self):
        return f"{self.volunteer.name} - {self.title}"
    

class VolunteerApplication(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)

    city = models.CharField(max_length=100)
    interest = models.CharField(max_length=255)   # multiple interests (comma separated)
    availability = models.CharField(max_length=50)
    reason = models.TextField()

    proof = models.FileField(upload_to="volunteer_proofs/")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    authorization_code = models.CharField(
        max_length=12,
        blank=True,
        null=True
    )

    applied_at = models.DateTimeField(auto_now_add=True)

    def generate_code(self):
        self.authorization_code = uuid.uuid4().hex[:10].upper()

