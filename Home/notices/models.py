from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Notice(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    semester = models.IntegerField(null=True, blank=True, help_text="Target semester (null = all)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class NoticeDismiss(models.Model):
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE, related_name='dismissals')
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    dismissed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('notice', 'student')