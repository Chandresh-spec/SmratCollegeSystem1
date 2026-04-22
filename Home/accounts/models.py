
from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class User(AbstractUser):
    ROLE_CHOICES = (
    ('student', 'Student'),
    ('faculty', 'Faculty'),
    ('admin', 'Admin'),
    )
    role=models.CharField(choices=ROLE_CHOICES,default='student',null=False,blank=False)
    mobile_number=models.CharField(max_length=12,null=True,blank=False)
    usn = models.CharField(max_length=20, unique=True, null=True, blank=True)
    sem=models.IntegerField(null=True,blank=True)

    def __str__(self):
        return f"{self.username} ->{self.usn}"