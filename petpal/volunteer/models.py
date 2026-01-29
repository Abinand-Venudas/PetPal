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

class VolunteerTask(models.Model):
    volunteer = models.ForeignKey(volunteer_registration, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    task_time = models.DateTimeField()
    status = models.CharField(max_length=30, choices=[
        ('upcoming', 'Upcoming'),
        ('completed', 'Completed')
    ], default='upcoming')

    def __str__(self):
        return f"{self.title} - {self.volunteer.name}"


class VolunteerPet(models.Model):
    volunteer = models.ForeignKey(volunteer_registration, on_delete=models.CASCADE)
    pet_name = models.CharField(max_length=100)
    species = models.CharField(max_length=50)
    assigned_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.pet_name

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
