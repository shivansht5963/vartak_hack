from django.urls import path
from .views import upload_file_view, get_job_status, n8n_callback_view, dashboard_view

urlpatterns = [
    path('api/upload/', upload_file_view, name='upload_file'),
    path('api/status/<uuid:job_id>/', get_job_status, name='job_status'),
    path('api/callback/<uuid:job_id>/', n8n_callback_view, name='n8n_callback'),
    path('dashboard/<uuid:job_id>/', dashboard_view, name='dashboard'),
]
