from django.contrib import admin
from .models import ETLJob, JobError

@admin.register(ETLJob)
class ETLJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'progress_percentage', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'status')
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(JobError)
class JobErrorAdmin(admin.ModelAdmin):
    list_display = ('job', 'row_index', 'error_message', 'timestamp')
    list_filter = ('job', 'timestamp')
    search_fields = ('job__id', 'error_message')
