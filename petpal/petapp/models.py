from django.db import models

# Create your models here.
class user_registration(models.Model):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100,default='True')
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.name