from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """Custom user model with additional fields"""
    first_name = models.CharField(max_length=30, blank=True, help_text="First name of the user")
    last_name = models.CharField(max_length=30, blank=True, help_text="Last name of the user")
    age = models.IntegerField(null=True, blank=True, help_text="Age of the user")
    gender = models.CharField(
        max_length=10,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
        ],
        null=True,
        blank=True,
        help_text="Gender of the user"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

class UserAnalysis(models.Model):
    """Store user analysis results"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    prediction_result = models.CharField(max_length=50)
    confidence_scores = models.FloatField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return f"Analysis {self.id} - {self.prediction_result}"
