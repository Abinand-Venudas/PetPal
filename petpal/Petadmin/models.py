from django.db import models

class Pro_Admin(models.Model):
    admin_name = models.CharField(max_length=100)
    admin_email = models.EmailField(unique=True)
    admin_password = models.CharField(max_length=100)

    def __str__(self):
        return self.admin_name
