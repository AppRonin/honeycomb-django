from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .tasks import long_task
from celery.result import AsyncResult

# Create your views here.
def home(request):
    return render(request, 'automation/home.html')

def about(request):
    return render(request, 'automation/about.html')

@login_required
def gpon_conversor(request):
    return render(request, 'automation/gpon_conversor.html')

def start_task(request):
    task = long_task.delay()
    return JsonResponse({"task_id": task.id})

def get_progress(request, task_id):
    result = AsyncResult(task_id)

    if result.state == "PENDING":
        progress = 0
    elif result.state == "PROGRESS":
        progress = result.info.get("progress", 0)
    elif result.state == "SUCCESS":
        progress = 100
    else:
        progress = 0

    return JsonResponse({
        "state": result.state,
        "progress": progress
    })