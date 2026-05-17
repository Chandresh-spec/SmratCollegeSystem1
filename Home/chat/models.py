from django.db import models
from django.contrib.auth import get_user_model
from Academic.models import Subject


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


class AnonChatRoom(models.Model):
    """A chat room tied to a subject — teacher sees all, students are anonymous."""
    subject = models.OneToOneField(Subject, on_delete=models.CASCADE, related_name='chat_room')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ChatRoom: {self.subject.sub_name}"


class AnonMessage(models.Model):
    room = models.ForeignKey(AnonChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    # Anonymous alias like "Student #4" — only used for students
    anon_alias = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def save(self, *args, **kwargs):
        if self.sender.role == 'student' and not self.anon_alias:
            # Deterministic anonymous name based on room + user id
            existing = AnonMessage.objects.filter(room=self.room, sender=self.sender).first()
            if existing:
                self.anon_alias = existing.anon_alias
            else:
                count = AnonMessage.objects.filter(room=self.room).values('sender').distinct().filter(sender__role='student').count()
                self.anon_alias = f"Student #{count + 1}"
        elif self.sender.role in ['faculty', 'admin']:
            self.anon_alias = f"Prof. {self.sender.username}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.anon_alias}: {self.content[:40]}"
