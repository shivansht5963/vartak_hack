# jobs/models.py
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
    row_index = models.IntegerField()
    error_message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

# --- ADD THIS NEW MODEL FOR SAKSHAM ---
class RowItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(ETLJob, on_delete=models.CASCADE, related_name='rows')
    
    # Raw Input
    raw_text = models.TextField(blank=True, null=True)
    
    # Feature 1: Ghost Data (AI + Web Search)
    enriched_data = models.JSONField(null=True, blank=True) 
    is_enriched = models.BooleanField(default=False)
    
    # Feature 2: Confidence Heatmap (0-100)
    confidence_score = models.IntegerField(default=0)
    
    status = models.CharField(max_length=20, default='PENDING', choices=[
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed')
    ])

    def __str__(self):
        return f"Row {self.id} - {self.confidence_score}%"