import argparse
from django.core.management.base import BaseCommand, CommandError
from utils.data_parser import MetOfficeParser


class Command(BaseCommand):
    help = 'Import weather data from UK MetOffice for specific parameters and regions. If no arguments are provided, imports all available data.'

    def add_arguments(self, parser):
        parser.add_argument('--parameter', type=str, help='Parameter code (e.g., Tmax)', required=False)
        parser.add_argument('--region', type=str, help='Region code (e.g., UK)', required=False)
        parser.add_argument('--all-regions', action='store_true', help='Import data for all available regions')
        parser.add_argument('--all-parameters', action='store_true', help='Import data for all available parameters')
        
    def handle(self, *args, **options):
        parameter_code = options.get('parameter')
        region_code = options.get('region')
        all_regions = options.get('all_regions', False)
        all_parameters = options.get('all_parameters', False)
        
        # If no specific parameter or region is provided, import all data
        if parameter_code is None and region_code is None and not all_regions and not all_parameters:
            self.stdout.write(self.style.NOTICE("No specific parameter or region provided. Importing all available data..."))
            all_parameters = True
            all_regions = True
        
        # Define available parameters and regions
        # These could be expanded to include all available options
        parameters = ['Tmax', 'Tmin', 'Tmean', 'Rainfall', 'Sunshine']
        regions = ['UK', 'England', 'Wales', 'Scotland', 'Northern_Ireland', 
                   'England_and_Wales', 'England_N', 'England_S', 'Scotland_N', 
                   'Scotland_E', 'Scotland_W', 'England_E_and_NE', 'England_NW_and_N_Wales',
                   'Midlands', 'East_Anglia', 'England_SW_and_S_Wales', 'England_SE_and_Central_S']
        
        # Determine which parameters to process
        if all_parameters:
            params_to_process = parameters
        elif parameter_code:
            params_to_process = [parameter_code]
        else:
            # If parameter is not specified but region is, use all parameters
            params_to_process = parameters
        
        # Determine which regions to process
        if all_regions:
            regions_to_process = regions
        elif region_code:
            regions_to_process = [region_code]
        else:
            # If region is not specified but parameter is, use all regions
            regions_to_process = regions
        
        parser = MetOfficeParser(max_retries=5, retry_delay=2)  # Use retry mechanism
        total_records = 0
        
        for param in params_to_process:
            for region in regions_to_process:
                try:
                    self.stdout.write(self.style.NOTICE(f"Importing data for parameter '{param}' and region '{region}'..."))
                    
                    # Fetch the data with retry mechanism
                    content = parser.fetch_data(param, region)
                    
                    # Parse the data
                    metadata, data = parser.parse_data(content)
                    
                    # Save to database
                    records_count = parser.save_to_database(param, region, metadata, data)
                    
                    # Print breakdown of data types
                    monthly_count = len([d for d in data if d.get('period_type') == 'monthly'])
                    annual_count = len([d for d in data if d.get('period_type') == 'ann'])
                    seasonal_count = len([d for d in data if d.get('period_type') in ['win', 'spr', 'sum', 'aut']])
                    
                    self.stdout.write(self.style.SUCCESS(
                        f"Successfully imported {records_count} records for {param} in {region} "
                        f"({monthly_count} monthly, {annual_count} annual, {seasonal_count} seasonal)"
                    ))
                    
                    total_records += records_count
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error importing data for {param} in {region}: {str(e)}"))
                    if not (all_parameters or all_regions):
                        raise CommandError(f"Import failed: {str(e)}")
        
        self.stdout.write(self.style.SUCCESS(f"Import completed. Total records imported: {total_records}"))
