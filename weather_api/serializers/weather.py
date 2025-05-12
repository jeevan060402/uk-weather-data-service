from rest_framework import serializers
from db.models import Region, Parameter, WeatherData


class RegionSerializer(serializers.ModelSerializer):
    """Serializer for the Region model"""
    class Meta:
        model = Region
        fields = ['id', 'code', 'name']


class ParameterSerializer(serializers.ModelSerializer):
    """Serializer for the Parameter model"""
    class Meta:
        model = Parameter
        fields = ['id', 'code', 'name', 'unit', 'description']


class WeatherDataSerializer(serializers.ModelSerializer):
    """Serializer for the WeatherData model with nested region and parameter details"""
    region = RegionSerializer(read_only=True)
    parameter = ParameterSerializer(read_only=True)
    period_display = serializers.SerializerMethodField()
    
    class Meta:
        model = WeatherData
        fields = ['id', 'region', 'parameter', 'year', 'period_type', 'month', 'value', 'anomaly', 'period_display']
    
    def get_period_display(self, obj):
        """Return a human-readable period string"""
        if obj.period_type == 'monthly' and obj.month:
            months = ['January', 'February', 'March', 'April', 'May', 'June', 
                     'July', 'August', 'September', 'October', 'November', 'December']
            return months[obj.month - 1]
        elif obj.period_type == 'ann':
            return 'Annual'
        elif obj.period_type == 'win':
            return 'Winter'
        elif obj.period_type == 'spr':
            return 'Spring'
        elif obj.period_type == 'sum':
            return 'Summer'
        elif obj.period_type == 'aut':
            return 'Autumn'
        return obj.period_type


class WeatherDataListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for WeatherData when returned as a list
    to reduce payload size
    """
    region_code = serializers.CharField(source='region.code', read_only=True)
    parameter_code = serializers.CharField(source='parameter.code', read_only=True)
    
    class Meta:
        model = WeatherData
        fields = ['id', 'region_code', 'parameter_code', 'year', 'period_type', 'month', 'value', 'anomaly']


class WeatherDataCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating WeatherData records"""
    region_code = serializers.SlugRelatedField(
        source='region',
        queryset=Region.objects.all(),
        slug_field='code'
    )
    parameter_code = serializers.SlugRelatedField(
        source='parameter',
        queryset=Parameter.objects.all(),
        slug_field='code'
    )
    
    class Meta:
        model = WeatherData
        fields = ['region_code', 'parameter_code', 'year', 'period_type', 'month', 'value', 'anomaly']
    
    def create(self, validated_data):
        region = validated_data.pop('region')
        parameter = validated_data.pop('parameter')
        
        return WeatherData.objects.create(
            region=region,
            parameter=parameter,
            **validated_data
        )
