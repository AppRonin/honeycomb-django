from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return render(request, 'automation/home.html')

def about(request):
    return render(request, 'automation/about.html')

@login_required
def gpon_conversor(request):
    return render(request, 'automation/gpon_conversor.html')