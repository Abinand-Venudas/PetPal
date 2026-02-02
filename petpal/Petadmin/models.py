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
    price = models.DecimalField(max_digits=8, decimal_places=2)

    # ✅ REQUIRED FIELDS (you were missing these)
    duration_days = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
