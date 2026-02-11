from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'automation/home.html')

def about(request):
    return render(request, 'automation/about.html')

def gpon_conversor(request):
    return render(request, 'automation/gpon_conversor.html')