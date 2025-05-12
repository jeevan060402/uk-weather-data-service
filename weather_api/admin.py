from django.contrib import admin

# Register your models here.
from django.contrib import admin
from db.models import Region, Parameter, WeatherData

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')
    ordering = ('name',)

@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'unit')
    search_fields = ('code', 'name')
    ordering = ('name',)

@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ('region', 'parameter', 'year', 'month', 'value')
    list_filter = ('region', 'parameter', 'year')
    search_fields = ('region__name', 'parameter__name')
    ordering = ('-year', '-month')
