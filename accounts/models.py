from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def save(self, *args, **kwargs):
        if not self.username:  
            self.username = self.email.split('@')[0]  # Set username to the part before '@' in email
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.username

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=25, default="")
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    role = models.CharField(max_length=20, choices=[('customer', 'Customer'), ('admin', 'Admin'), ('vendor', 'Vendor')], default='customer')
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"