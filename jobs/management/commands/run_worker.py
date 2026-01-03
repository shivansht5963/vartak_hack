import time
import requests
import os
import pytesseract
from PIL import Image
from pypdf import PdfReader
from django.core.management.base import BaseCommand
from jobs.models import ETLJob, RowItem

# !!! PASTE YOUR N8N URL HERE !!!
N8N_WEBHOOK_URL = "https://your-n8n-url.com/webhook/process-data" 

class Command(BaseCommand):
    help = 'Saksham Worker: Processes Jobs and Rows'

    def handle(self, *args, **kwargs):
        self.stdout.write("🚀 Saksham Worker Started... Waiting for jobs.")
        
        while True:
            # 1. Check for new File Uploads (Job Pending)
            new_job = ETLJob.objects.filter(status='PENDING').first()
            if new_job:
                self.process_file(new_job)
            
            # 2. Check for Rows waiting for AI (Row Pending)
            pending_row = RowItem.objects.filter(status='PENDING').first()
            if pending_row:
                self.send_to_n8n(pending_row)
            else:
                if not new_job:
                    time.sleep(2)

    def process_file(self, job):
        self.stdout.write(f"📂 Processing File for Job {job.id}...")
        try:
            file_path = job.original_file.path
            text_content = ""
            
            # 1. OCR for Images
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                text_content = pytesseract.image_to_string(Image.open(file_path))
            
            # 2. PDF Reader
            elif file_path.lower().endswith('.pdf'):
                reader = PdfReader(file_path)
                for page in reader.pages:
                    text_content += page.extract_text() + "\n"
            
            # 3. Text Files
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text_content = f.read()

            # Chunking logic
            lines = [line.strip() for line in text_content.split('\n') if len(line.strip()) > 5]
            
            if not lines:
                lines = ["No readable text found."]

            for line in lines:
                RowItem.objects.create(job=job, raw_text=line, status='PENDING')
            
            job.status = 'PROCESSING'
            job.save()
            self.stdout.write(self.style.SUCCESS(f"✅ Created {len(lines)} rows."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))
            job.status = 'FAILED'
            job.save()

    def send_to_n8n(self, row):
        self.stdout.write(f"📡 Sending Row {row.id}...")
        row.status = 'PROCESSING'
        row.save()
        
        payload = {"id": str(row.id), "text": row.raw_text}
        
        try:
            requests.post(N8N_WEBHOOK_URL, json=payload, timeout=10)
            self.stdout.write(self.style.SUCCESS("--> Sent"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"--> Error: {e}"))
            row.status = 'FAILED'
            row.save()
        
        time.sleep(2)