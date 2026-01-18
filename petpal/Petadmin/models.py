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
    icon = models.CharField(
        max_length=50,
        help_text="FontAwesome icon class (e.g. fa-shower, fa-scissors)"
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
