import json
import requests
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import ETLJob, RowItem, JobError

@csrf_exempt
def upload_file_view(request):
    """
    Step 1: User uploads a file. We just save it.
    The Worker Script (Person 3) will verify it and split it into rows later.
    """
    if request.method == 'POST' and request.FILES.get('original_file'):
        uploaded_file = request.FILES['original_file']
        job = ETLJob.objects.create(original_file=uploaded_file)
        return JsonResponse({'job_id': job.id}, status=201)
    
    return JsonResponse({'error': 'Invalid request. POST a file named "original_file".'}, status=400)

@csrf_exempt
@require_POST
def update_row_api(request):
    """
    Step 4: n8n calls this API when it finishes analyzing ONE row.
    Expected JSON Payload:
    {
        "id": "row_uuid",
        "enriched_data": { "name": "...", "ceo": "..." },
        "confidence_score": 85,
        "is_enriched": true
    }
    """
    try:
        data = json.loads(request.body)
        row_id = data.get('id')
        
        row = get_object_or_404(RowItem, id=row_id)
        
        # Save Saksham AI Data
        row.enriched_data = data.get('enriched_data')
        row.confidence_score = data.get('confidence_score', 0)
        row.is_enriched = data.get('is_enriched', False)
        row.status = 'COMPLETED'
        row.save()
        
        # Update Job Progress Percentage
        total_rows = row.job.rows.count()
        completed_rows = row.job.rows.filter(status='COMPLETED').count()
        
        if total_rows > 0:
            row.job.progress_percentage = int((completed_rows / total_rows) * 100)
            
            # If all rows are done, mark job as completed
            if completed_rows == total_rows:
                row.job.status = 'COMPLETED'
            else:
                row.job.status = 'PROCESSING'
            row.job.save()

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def dashboard_view(request, job_id):
    """
    The Saksham Dashboard. Shows the Heatmap.
    """
    job = get_object_or_404(ETLJob, id=job_id)
    
    # Get all rows, ordered by confidence (Riskier rows first?)
    # Let's order by creation so they match the file order
    rows = job.rows.all().order_by('id')
    
    # Calculate Stats
    completed = rows.filter(status='COMPLETED').count()
    avg_conf = 0
    if completed > 0:
        total_score = sum([r.confidence_score for r in rows if r.status == 'COMPLETED'])
        avg_conf = round(total_score / completed, 1)

    context = {
        'job': job,
        'rows': rows,
        'stats': {
            'total': rows.count(),
            'completed': completed,
            'avg_conf': avg_conf
        }
    }
    return render(request, 'jobs/dashboard.html', context)

# Keep other views if necessary (e.g. get_job_status), or remove if unused.
def get_job_status(request, job_id):
    job = get_object_or_404(ETLJob, id=job_id)
    return JsonResponse({"status": job.status, "progress": job.progress_percentage})

@csrf_exempt
def n8n_callback_view(request, job_id):
    # This was the old view. You can keep it or delete it.
    # update_row_api replaces its functionality for rows.
    return JsonResponse({"status": "deprecated"})

def simple_upload_view(request):
    return render(request, 'jobs/upload.html')