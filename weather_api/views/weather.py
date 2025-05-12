from rest_framework import viewsets, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer

from db.models import Region, Parameter, WeatherData
from weather_api.serializers.weather import (
    RegionSerializer, 
    ParameterSerializer, 
    WeatherDataSerializer,
    WeatherDataListSerializer,
    WeatherDataCreateSerializer
)
from utils.data_parser import MetOfficeParser


class RegionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows regions to be viewed or edited.
    """
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['code', 'name']


class ParameterViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows weather parameters to be viewed or edited.
    """
    queryset = Parameter.objects.all()
    serializer_class = ParameterSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['code', 'name']


class WeatherDataViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows weather data to be viewed or edited.
    """
    queryset = WeatherData.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['region__code', 'parameter__code', 'year', 'period_type', 'month']
    ordering_fields = ['year', 'period_type', 'month', 'value']
    ordering = ['-year', 'period_type', '-month']
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return WeatherDataListSerializer
        elif self.action == 'create':
            return WeatherDataCreateSerializer
        return WeatherDataSerializer
    
    @action(detail=False, methods=['get'], url_path='by-region-parameter/(?P<region_code>[^/.]+)/(?P<parameter_code>[^/.]+)')
    def by_region_parameter(self, request, region_code=None, parameter_code=None):
        """
        Retrieve weather data for a specific region and parameter.
        
        Optionally filter by start_year, end_year, and period_type query parameters.
        """
        queryset = self.queryset.filter(
            region__code=region_code,
            parameter__code=parameter_code
        )
        
        # Apply year range filters if provided
        start_year = request.query_params.get('start_year')
        if start_year:
            queryset = queryset.filter(year__gte=int(start_year))
            
        end_year = request.query_params.get('end_year')
        if end_year:
            queryset = queryset.filter(year__lte=int(end_year))
        
        # Apply period type filter if provided
        period_type = request.query_params.get('period_type')
        if period_type:
            queryset = queryset.filter(period_type=period_type)
            
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = WeatherDataListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = WeatherDataListSerializer(queryset, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'], url_path='seasonal/(?P<region_code>[^/.]+)/(?P<parameter_code>[^/.]+)')
    def seasonal_data(self, request, region_code=None, parameter_code=None):
        """
        Retrieve seasonal weather data for a specific region and parameter.
        
        Optionally filter by start_year and end_year query parameters.
        """
        queryset = self.queryset.filter(
            region__code=region_code,
            parameter__code=parameter_code,
            period_type__in=['win', 'spr', 'sum', 'aut']
        )
        
        # Apply year range filters if provided
        start_year = request.query_params.get('start_year')
        if start_year:
            queryset = queryset.filter(year__gte=int(start_year))
            
        end_year = request.query_params.get('end_year')
        if end_year:
            queryset = queryset.filter(year__lte=int(end_year))
            
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = WeatherDataListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = WeatherDataListSerializer(queryset, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'], url_path='annual/(?P<region_code>[^/.]+)/(?P<parameter_code>[^/.]+)')
    def annual_data(self, request, region_code=None, parameter_code=None):
        """
        Retrieve annual weather data for a specific region and parameter.
        
        Optionally filter by start_year and end_year query parameters.
        """
        queryset = self.queryset.filter(
            region__code=region_code,
            parameter__code=parameter_code,
            period_type='ann'
        )
        
        # Apply year range filters if provided
        start_year = request.query_params.get('start_year')
        if start_year:
            queryset = queryset.filter(year__gte=int(start_year))
            
        end_year = request.query_params.get('end_year')
        if end_year:
            queryset = queryset.filter(year__lte=int(end_year))
            
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = WeatherDataListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = WeatherDataListSerializer(queryset, many=True)
        return Response(serializer.data)


class ImportWeatherDataView(APIView):
    """
    API endpoint to import weather data from the MetOffice.
    """
    def post(self, request):
        """
        Import weather data from the MetOffice for a given parameter and region.
        """
        parameter_code = request.data.get('parameter_code')
        region_code = request.data.get('region_code')
        
        if not parameter_code or not region_code:
            return Response(
                {"error": "Both parameter_code and region_code are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        parser = MetOfficeParser()
        
        try:
            # Fetch the data
            content = parser.fetch_data(parameter_code, region_code)
            
            # Parse the data
            metadata, data = parser.parse_data(content)
            
            # Save to database
            records_count = parser.save_to_database(parameter_code, region_code, metadata, data)
            
            return Response({
                "success": True,
                "message": f"Data imported successfully for {parameter_code} in {region_code}",
                "records_imported": records_count
            })
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
