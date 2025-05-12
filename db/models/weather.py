from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Region(models.Model):
    """
    Represents a geographical region for which weather data is available.
    Examples: UK, England, Scotland, etc.
    """
    code = models.CharField(max_length=20, unique=True, help_text="Region code as used in MetOffice URLs")
    name = models.CharField(max_length=100, help_text="Full name of the region")
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Parameter(models.Model):
    """
    Represents a weather parameter that can be measured.
    Examples: Tmax (maximum temperature), Rainfall, etc.
    """
    code = models.CharField(max_length=20, unique=True, help_text="Parameter code as used in MetOffice URLs")
    name = models.CharField(max_length=100, help_text="Full name of the parameter")
    unit = models.CharField(max_length=20, help_text="Unit of measurement")
    description = models.TextField(null=True, blank=True, help_text="Optional description of the parameter")
    
    def __str__(self):
        return f"{self.name} ({self.unit})"
    
    class Meta:
        ordering = ['name']


class WeatherData(models.Model):
    """
    Represents a weather data point for a specific region, parameter, year, and period.
    """
    # Period types
    PERIOD_MONTHLY = 'monthly'
    PERIOD_SEASONAL_WINTER = 'win'
    PERIOD_SEASONAL_SPRING = 'spr'
    PERIOD_SEASONAL_SUMMER = 'sum'
    PERIOD_SEASONAL_AUTUMN = 'aut'
    PERIOD_ANNUAL = 'ann'
    
    PERIOD_CHOICES = [
        (PERIOD_MONTHLY, 'Monthly'),
        (PERIOD_SEASONAL_WINTER, 'Winter'),
        (PERIOD_SEASONAL_SPRING, 'Spring'),
        (PERIOD_SEASONAL_SUMMER, 'Summer'),
        (PERIOD_SEASONAL_AUTUMN, 'Autumn'),
        (PERIOD_ANNUAL, 'Annual'),
    ]
    
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='weather_data')
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE, related_name='weather_data')
    year = models.IntegerField(validators=[MinValueValidator(1800), MaxValueValidator(2100)])
    period_type = models.CharField(
        max_length=10, 
        choices=PERIOD_CHOICES,
        default=PERIOD_MONTHLY,
        help_text="Type of period this data represents (monthly, seasonal, or annual)"
    )
    month = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)], 
        null=True, 
        blank=True,
        help_text="Month number (1-12). Used only for monthly data."
    )
    value = models.FloatField(help_text="The measured value")
    anomaly = models.FloatField(null=True, blank=True, help_text="Anomaly from reference period if available")
    
    def __str__(self):
        if self.period_type == self.PERIOD_MONTHLY and self.month:
            period_str = f"-{self.month:02d}"
        else:
            period_str = f"-{self.period_type}"
        return f"{self.region.code} - {self.parameter.code} - {self.year}{period_str}: {self.value}"
    
    class Meta:
        ordering = ['-year', 'period_type', '-month']
        unique_together = ['region', 'parameter', 'year', 'period_type', 'month']
        verbose_name_plural = "Weather Data"
        indexes = [
            models.Index(fields=['region', 'parameter', 'year', 'period_type', 'month']),
            models.Index(fields=['year', 'period_type', 'month']),
        ]
