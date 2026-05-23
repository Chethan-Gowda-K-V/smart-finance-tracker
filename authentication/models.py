from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    currency = models.CharField(max_length=3, default='USD')
    monthly_income_goal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.username
