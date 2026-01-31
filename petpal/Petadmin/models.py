from django.db import models
# =========================
# SERVICE MODEL

class Pro_Admin(models.Model):
    admin_name = models.CharField(max_length=100)
    admin_email = models.EmailField(unique=True)
    admin_password = models.CharField(max_length=100)

    def __str__(self):
        return self.admin_name
    
class GroomingService(models.Model):
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    icon = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class DaycarePlan(models.Model):
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    duration_days = models.PositiveIntegerField(help_text="Number of days")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.duration_days} days)"
