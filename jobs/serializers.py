from rest_framework import serializers
from .models import ETLJob, JobError

class ETLJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = ETLJob
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'process_percentage') 
        # Note: progress_percentage is usually updated by the backend/worker, so maybe read-only for input, 
        # but the prompt implies sending JSON data back, so standard __all__ is fine. 
        # I'll stick to 'fields = "__all__"' as a safe bet for "complete code".

class JobErrorSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobError
        fields = '__all__'
