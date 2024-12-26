from django.db import models

from django.contrib.auth.models import User

# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    newsletter = models.BooleanField(default=False)
    
    
    def __str__(self) -> str:
        return self.user




