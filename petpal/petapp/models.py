from django.db import models
from doctor.models import doctor_registration
from volunteer.models import volunteer_registration
from django.utils import timezone
from datetime import timedelta


# =========================
# USER MODEL
# =========================
class user_registration(models.Model):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.name


# =========================
# PET MODEL
# =========================
class Pet(models.Model):
    STATUS_CHOICES = [
        ("available", "Available"),
        ("adopted", "Adopted"),
        ("hidden", "Hidden"),
    ]

    name = models.CharField(max_length=100)
    pet_type = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='pet_images/', blank=True, null=True)
    vaccinated = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")

    def __str__(self):
        return self.name


# =========================
# ADOPTION REQUEST
# =========================
class AdoptionRequest(models.Model):
    user = models.ForeignKey(user_registration, on_delete=models.CASCADE)
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)

    status = models.CharField(
        max_length=20,
        choices=[("Pending", "Pending"), ("Approved", "Approved"), ("Rejected", "Rejected")],
        default="Pending"
    )

    visit_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} → {self.pet.name} ({self.status})"


# =========================
# CONSULTATION / APPOINTMENT
# =========================
class Consultation(models.Model):
    user = models.ForeignKey(user_registration, on_delete=models.CASCADE)
    doctor = models.ForeignKey(doctor_registration, on_delete=models.CASCADE)

    pet_name = models.CharField(max_length=100, null=True, blank=True)
    pet_type = models.CharField(max_length=50, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)

    issue = models.TextField()
    date = models.DateField()
    time = models.TimeField()

    status = models.CharField(
        max_length=20,
        choices=[("Pending","Pending"),("Approved","Approved"),
                 ("Completed","Completed"),("Rejected","Rejected")],
        default="Pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("doctor", "date", "time")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.name} → Dr. {self.doctor.name} ({self.date} @ {self.time})"


# =========================
# TEMP SLOT LOCK (DOCTOR)
# =========================
class SlotLock(models.Model):
    doctor = models.ForeignKey(doctor_registration, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(user_registration, on_delete=models.CASCADE, null=True, blank=True)

    date = models.DateField()
    time = models.TimeField()
    locked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("doctor", "date", "time")

    def is_expired(self):
        return timezone.now() > self.locked_at + timedelta(minutes=5)

    def __str__(self):
        return f"LOCK → Dr. {self.doctor.name if self.doctor else 'N/A'} | {self.date} @ {self.time}"


# =========================
# PASSWORD RESET OTP
# =========================
class PasswordResetOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)

    def is_valid(self):
        return timezone.now() <= self.created_at + timezone.timedelta(minutes=5)

    def __str__(self):
        return f"{self.email} - {self.otp}"


# =========================
# DAYCARE SLOT LOCK
# =========================
class DaycareSlotLock(models.Model):
    user = models.ForeignKey(user_registration, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    locked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("date", "time")

    def is_expired(self):
        return timezone.now() > self.locked_at + timedelta(minutes=5)


# =========================
# DAYCARE BOOKING
# =========================
class DaycareBooking(models.Model):
    user = models.ForeignKey(user_registration, on_delete=models.CASCADE)

    pet_name = models.CharField(max_length=100)
    pet_type = models.CharField(max_length=50)
    other_animal = models.CharField(max_length=100, blank=True, null=True)

    plan = models.CharField(max_length=50)
    duration = models.CharField(max_length=50)

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    total_cost = models.DecimalField(max_digits=8, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=[
            ("Pending","Pending"),
            ("Confirmed","Confirmed"),
            ("Completed","Completed"),
            ("Cancelled","Cancelled"),
        ],
        default="Confirmed"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("date", "start_time")


# =========================
# GROOMING SERVICE
# =========================
class Service(models.Model):
    SERVICE_TYPE_CHOICES = (
        ("grooming", "Grooming"),
        ("daycare", "Daycare"),
    )

    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    duration = models.CharField(max_length=50, blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    service_type = models.CharField(
        max_length=20,
        choices=SERVICE_TYPE_CHOICES,
        default="grooming"
    )

    # ✅ ADD THIS
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.service_type})"



# =========================
# GROOMING SLOT LOCK (ANTI-RACE)
# =========================
class GroomingSlotLock(models.Model):
    user = models.ForeignKey(user_registration, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    locked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("date", "time")

    def is_expired(self):
        return timezone.now() > self.locked_at + timedelta(minutes=5)

    def __str__(self):
        return f"GROOM LOCK → {self.date} @ {self.time}"


# =========================
# GROOMING BOOKING MODEL (UPDATED)
# =========================
class GroomingBooking(models.Model):
    user = models.ForeignKey(user_registration, on_delete=models.CASCADE)

    volunteer = models.ForeignKey(
        volunteer_registration,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # ===== PET DETAILS =====
    animal_type = models.CharField(max_length=50)
    pet_name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    condition = models.CharField(max_length=200, blank=True, null=True)

    # ===== GUARDIAN DETAILS =====
    guardian_name = models.CharField(max_length=100)
    guardian_phone = models.CharField(max_length=15)
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    # ===== BOOKING DETAILS =====
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    services = models.JSONField()
    total = models.IntegerField()
    total_duration = models.IntegerField()

    instructions = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=30,
        choices=[
            ("Pending", "Pending"),
            ("Assigned", "Assigned"),
            ("In Progress", "In Progress"),
            ("Completed", "Completed"),
            ("Cancelled", "Cancelled"),
        ],
        default="Pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("date", "start_time")  # 🔒 HARD booking protection

    def __str__(self):
        return f"GROOMING → {self.pet_name} | {self.date} {self.start_time}"
