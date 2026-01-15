from django.db import models

# Create your models here.
class doctor_registration(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)

    city = models.CharField(max_length=50, blank=True, null=True)
    specialization = models.CharField(max_length=50, blank=True, null=True)

    experience = models.IntegerField(blank=True, null=True)

    license = models.CharField(max_length=50, blank=True, null=True)
    clinic = models.CharField(max_length=100, blank=True, null=True)

    image = models.ImageField(upload_to='doctorImages/', blank=True, null=True)

    password = models.CharField(max_length=128)

    is_active = models.BooleanField(default=True)
    is_checkout = models.BooleanField(default=True)
    is_available = models.BooleanField(default=False) 

    def __str__(self):
        return self.name


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    # ✅ USE STRING REFERENCES (NO IMPORTS)
    user = models.ForeignKey("petapp.user_registration", on_delete=models.CASCADE)
    doctor = models.ForeignKey("doctor.doctor_registration", on_delete=models.CASCADE)

    pet_name = models.CharField(max_length=100)
    pet_type = models.CharField(max_length=50)
    reason = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pet_name} | {self.date} {self.time} | Dr. {self.doctor.name}"
