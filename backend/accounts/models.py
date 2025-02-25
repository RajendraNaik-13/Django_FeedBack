from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        MODERATOR = 'MODERATOR', 'Moderator'
        CONTRIBUTOR = 'CONTRIBUTOR', 'Contributor'
    
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.CONTRIBUTOR,
    )
    
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures', blank=True, null=True)
    
    def is_admin(self):
        return self.role == self.Role.ADMIN
    
    def is_moderator(self):
        return self.role == self.Role.MODERATOR
    
    def is_contributor(self):
        return self.role == self.Role.CONTRIBUTOR
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"