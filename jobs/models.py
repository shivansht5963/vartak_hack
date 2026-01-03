from django.db import models
import uuid

class ETLJob(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_file = models.FileField(upload_to='uploads/')
    processed_file = models.FileField(upload_to='processed/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    progress_percentage = models.IntegerField(default=0)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Job {self.id} - {self.status}"

class JobError(models.Model):
    job = models.ForeignKey(ETLJob, on_delete=models.CASCADE, related_name='errors')
    row_index = models.IntegerField(help_text="Which row number failed?")
    error_message = models.TextField(help_text="What went wrong?")
    raw_data = models.TextField(help_text="The actual bad data from that row")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Error in Job {self.job.id} at Row {self.row_index}"
