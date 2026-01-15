from django.db import models

# Create your models here.
class volunteer_registration(models.Model):
    name = models.CharField(max_length=100)
    # username = models.CharField(max_length=100, default='True')
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    proof = models.FileField(upload_to='volunteer_docs',default=True)
    phone = models.CharField(max_length=15, default='True')
    skills = models.CharField(max_length=30, default='True')
    address = models.TextField(default='True')
    is_available = models.BooleanField(default=False) 

    
    def __str__(self):
        return self.name