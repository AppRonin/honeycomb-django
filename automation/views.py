import re 
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage

from .tasks import gpon_conversor_task
from celery.result import AsyncResult

# Create your views here.
def home(request):
    return render(request, 'automation/home.html')

def about(request):
    return render(request, 'automation/about.html')

@login_required
def gpon_conversor(request):
    PORT_PATTERN = r"^\d+\/\d+\/\d+$" # 1/1/1
    MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB

    if request.method == "POST":
        uploaded_file = request.FILES.get("file")
        port = request.POST.get("port")

        if not uploaded_file:
            return JsonResponse({"error": "No file provided"}, status=400)

        if uploaded_file.size > MAX_FILE_SIZE:
            return JsonResponse({"error": "File too large. Max size is 2MB"}, status=400)

        # Allow only .txt
        if not uploaded_file.name.lower().endswith(".txt"):
            return JsonResponse({"error": "Only .txt files are allowed"}, status=400)

        # Validate port
        if not port or not re.match(PORT_PATTERN, port):
            return JsonResponse({"error": "Invalid port format"}, status=400)
        
        file_path = default_storage.save(f"uploads/{uploaded_file.name}", uploaded_file)

        task = gpon_conversor_task.delay(file_path, port)

        return JsonResponse({"task_id": task.id})
    
    return render(request, 'automation/gpon_conversor.html')


def task_progress(request, task_id):
    result = AsyncResult(task_id)

    if result.state == "PROGRESS":
        return JsonResponse(result.info)

    if result.state == "SUCCESS":
        return JsonResponse({
            "progress": 100,
            "template": result.result["template"]
        })

    if result.state == "FAILURE":
        return JsonResponse({
            "error": str(result.info)
        })

    return JsonResponse({"progress": 0})