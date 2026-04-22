from django.db import models
from django.contrib.auth import get_user_model
from Academic.models import Sem

User = get_user_model()


class Notice(models.Model):

    TYPE_CHOICES = (
        ('GENERAL', 'General'),
        ('URGENT', 'Urgent'),
        ('INFO', 'Info'),
    )

    title = models.CharField(max_length=255,null=True,blank=True)
    message = models.TextField(null=True,blank=True)

    notice_type = models.CharField(max_length=20, choices=TYPE_CHOICES,null=True,blank=True)

    semester = models.ForeignKey(
        Sem,
        on_delete=models.CASCADE,
        related_name="notices",null=True,blank=True
    )

    posted_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'faculty'},
        null=True,blank=True
    )

    is_active = models.BooleanField(default=True,null=True,blank=True)

    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)

    def __str__(self):
        return self.title
    



class NoticeDismiss(models.Model):
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE,null=True,blank=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)

    dismissed_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)

    class Meta:
        unique_together = ('notice', 'student')