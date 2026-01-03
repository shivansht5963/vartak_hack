import json
import requests
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import ETLJob, JobError

# Placeholder for n8n Webhook URL - Replace with actual URL
N8N_WEBHOOK_URL = "https://your-n8n-instance.com/webhook/..."

@csrf_exempt
def upload_file_view(request):
    if request.method == 'POST' and request.FILES.get('original_file'):
        uploaded_file = request.FILES['original_file']
        
        # Create Job
        job = ETLJob.objects.create(original_file=uploaded_file)
        
        # Construct absolute URL for the file
        # request.build_absolute_uri returns the full domain + path
        file_url = request.build_absolute_uri(job.original_file.url)
        
        # Payload for n8n
        payload = {
            'job_id': str(job.id),
            'file_url': file_url,
            'metadata': job.metadata
        }
        
        # Send to n8n
        try:
            # Using a generic error catch to prevent user view crash if n8n is down
            response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=5)
            # You might want to log response.status_code here
        except requests.exceptions.RequestException as e:
            # In a real app, handle this (retry, log error, etc.)
            print(f"Failed to trigger n8n: {e}")
            
        return JsonResponse({'job_id': job.id}, status=201)
    
    return JsonResponse({'error': 'Invalid request. POST a file named "original_file".'}, status=400)

def get_job_status(request, job_id):
    job = get_object_or_404(ETLJob, id=job_id)
    
    # Get all related error messages
    # Assuming 'related_name="errors"' was set on theForeignKey in JobError model
    # If not, use job.joberror_set.all()
    # Based on my previous turn, I used related_name='errors'.
    errors = list(job.errors.values_list('error_message', flat=True))
    
    response_data = {
        "status": job.status,
        "progress": job.progress_percentage,
        "errors": errors
    }
    return JsonResponse(response_data)

@csrf_exempt
def n8n_callback_view(request, job_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            job = get_object_or_404(ETLJob, id=job_id)
            
            # Update fields if present
            if 'status' in data:
                job.status = data['status']
            if 'progress' in data:
                job.progress_percentage = data['progress']
            
            job.save()
            
            # Handle new error logic
            new_error = data.get('new_error')
            if new_error:
                # Basic logging, assuming row_index might be passed or default to 0/1
                # The prompt example: "new_error": "Row 5 bad date"
                # If we want to split this or just save it as message:
                JobError.objects.create(
                    job=job,
                    row_index=data.get('row_index', 0), # Default 0 if not provided
                    error_message=new_error,
                    raw_data=data.get('raw_data', 'N/A') # Optional extra data
                )
                
            return JsonResponse({"success": True})
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'error': 'POST method required'}, status=405)

def dashboard_view(request, job_id):
    job = get_object_or_404(ETLJob, id=job_id)
    return render(request, 'jobs/dashboard.html', {'job': job})
