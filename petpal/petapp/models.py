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

    # 🔥 NEW FIELDS
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
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="available"
    )

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
        choices=[
            ("Pending", "Pending"),
            ("Approved", "Approved"),
            ("Rejected", "Rejected")
        ],
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

    # Pet details (optional)
    pet_name = models.CharField(max_length=100, null=True, blank=True)
    pet_type = models.CharField(max_length=50, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)

    issue = models.TextField()
    date = models.DateField()
    time = models.TimeField()

    status = models.CharField(
        max_length=20,
        choices=[
            ("Pending", "Pending"),
            ("Approved", "Approved"),
            ("Completed", "Completed"),
            ("Rejected", "Rejected")
        ],
        default="Pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 🚫 Prevent double booking of the same doctor at same date & time
        unique_together = ("doctor", "date", "time")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.name} → Dr. {self.doctor.name} ({self.date} @ {self.time})"


# =========================
# TEMPORARY SLOT LOCK (ANTI-RACE CONDITION)
# =========================
class SlotLock(models.Model):
    doctor = models.ForeignKey(
        doctor_registration,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        user_registration,
        on_delete=models.CASCADE,
        null=True,          # 👈 ADD THIS
        blank=True
    )

    date = models.DateField()
    time = models.TimeField()
    locked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevent two users from locking same slot at same time
        unique_together = ("doctor", "date", "time")

    def is_expired(self):
        return timezone.now() > self.locked_at + timedelta(minutes=5)

    def __str__(self):
        return f"LOCK → Dr. {self.doctor.name if self.doctor else 'N/A'} | {self.date} @ {self.time}"

# =========================
# PASSWORD RESET OTP MODEL
class PasswordResetOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)

    def is_valid(self):
        return timezone.now() <= self.created_at + timezone.timedelta(minutes=5)

    def __str__(self):
        return f"{self.email} - {self.otp}"
    
# =========================
# DAYCARE BOOKING
# =========================
class DaycareBooking(models.Model):
    user = models.ForeignKey(user_registration, on_delete=models.CASCADE)

    pet_name = models.CharField(max_length=100)
    pet_type = models.CharField(max_length=50, null=True, blank=True)

    plan = models.CharField(max_length=50)   # Standard / Premium / Full Day
    duration = models.CharField(max_length=50)  # Half Day / Full Day

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    total_cost = models.DecimalField(max_digits=8, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=[
            ("Pending", "Pending"),
            ("Confirmed", "Confirmed"),
            ("Completed", "Completed"),
            ("Cancelled", "Cancelled")
        ],
        default="Confirmed"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} → {self.pet_name} ({self.date})"

class Service(models.Model):
    name = models.CharField(max_length=100)
    price = models.CharField(max_length=100)

    # ✅ NEW FIELD
    icon = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="Emoji icon for the service (e.g. 🛁 ✂️ 💅)"
    )

    def __str__(self):
        return self.name

# =========================
# GROOMING BOOKING MODEL
# =========================
class GroomingBooking(models.Model):
    user = models.ForeignKey(user_registration, on_delete=models.CASCADE)

    date = models.DateField()
    time = models.TimeField()

    phone = models.CharField(max_length=15)

    services = models.JSONField()   # list of service IDs
    total = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 🚫 Prevent double booking same slot
        unique_together = ("date", "time")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.name} → Grooming ({self.date} @ {self.time})"
