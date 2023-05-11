from django.db import models

# Create your models here.
class AuthUser(models.Model):
    user = models.ForeignKey(
        User,
    )
