from django.db import models
from django.contrib.auth import get_user_model


# Create your models here.
User=get_user_model()

class ChatSubject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class PDFDocument(models.Model):
    subject = models.ForeignKey(ChatSubject, on_delete=models.CASCADE)
    file = models.FileField(upload_to="pdfs/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
