from django.urls import path, include
from rest_framework.routers import DefaultRouter
from weather_api.views.weather import (
    RegionViewSet, 
    ParameterViewSet, 
    WeatherDataViewSet,
    ImportWeatherDataView
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'regions', RegionViewSet)
router.register(r'parameters', ParameterViewSet)
router.register(r'weather-data', WeatherDataViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
    path('import-data/', ImportWeatherDataView.as_view(), name='import-data'),
    path('weather-data/by-region-parameter/<str:region_code>/<str:parameter_code>/', 
         WeatherDataViewSet.as_view({'get': 'by_region_parameter'}), 
         name='weather-data-by-region-parameter'),
    path('weather-data/seasonal/<str:region_code>/<str:parameter_code>/', 
         WeatherDataViewSet.as_view({'get': 'seasonal_data'}), 
         name='weather-data-seasonal'),
    path('weather-data/annual/<str:region_code>/<str:parameter_code>/', 
         WeatherDataViewSet.as_view({'get': 'annual_data'}), 
         name='weather-data-annual'),
]