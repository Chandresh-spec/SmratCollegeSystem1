from django.db import models
from django.contrib.auth import get_user_model
from Academic.models import Subject

User = get_user_model()


class Resource(models.Model):

    FILE_TYPES = (
        ('PDF', 'PDF'),
        ('PPT', 'PPT'),
        ('DOC', 'DOC'),
        ('IMG', 'Image'),
    )

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='resources/', blank=True, null=True)
    reference_url = models.URLField(blank=True, null=True)

    file_type = models.CharField(max_length=10, choices=FILE_TYPES)

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="resources")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    is_official = models.BooleanField(default=False)

    view_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Auto-approve if faculty or admin
        if self.uploaded_by.role in ['faculty', 'admin']:
            self.status = 'APPROVED'
            self.is_official = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    


class ResourceDownload(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    downloaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'resource')