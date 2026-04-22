from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Sem(models.Model):
    sem_nmbr = models.IntegerField(unique=True)

    def __str__(self):
        return f"Semester {self.sem_nmbr}"


class Subject(models.Model):
    sub_code = models.CharField(max_length=20, unique=True)
    sub_name = models.CharField(max_length=100)
    sem = models.ForeignKey(Sem, on_delete=models.CASCADE, related_name="subjects")
    faculty = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'faculty'}
    )

    def __str__(self):
        return f"{self.sub_code} - {self.sub_name}"