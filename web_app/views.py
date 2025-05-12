from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from db.models import Region, Parameter, WeatherData

def home(request):
    """Home page view"""
    return render(request, 'home.html')

def dashboard(request):
    """Dashboard view with summary statistics and visualizations"""
    return render(request, 'dashboard.html')

def data_explorer(request):
    """Interactive data explorer view"""
    return render(request, 'data_explorer.html')

def stats_api(request):
    """API endpoint to return statistics about the database"""
    stats = {
        'regions_count': Region.objects.count(),
        'parameters_count': Parameter.objects.count(),
        'data_count': WeatherData.objects.count(),
        'last_updated': timezone.now().isoformat(),
    }
    return JsonResponse(stats)