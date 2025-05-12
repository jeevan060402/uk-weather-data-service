import pandas as pd
import requests
import re
import io
import time
import logging
from typing import Dict, List, Tuple, Optional
from django.conf import settings
from db.models import Region, Parameter, WeatherData


logger = logging.getLogger(__name__)


class MetOfficeParser:
    """
    Parser for UK MetOffice weather data files.
    
    Handles fetching and parsing data from the MetOffice website in various formats
    and converting them to structured data for storage in the database.
    """
    
    def __init__(self, max_retries=3, retry_delay=1):
        self.base_url = settings.METOFFICE_BASE_URL
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def fetch_data(self, parameter_code: str, region_code: str) -> str:
        """
        Fetch data from the MetOffice website for a given parameter and region.
        
        Args:
            parameter_code: The code for the parameter (e.g., 'Tmax')
            region_code: The code for the region (e.g., 'UK')
            
        Returns:
            The text content of the file
            
        Raises:
            requests.RequestException: If the request fails after all retries
        """
        url = f"{self.base_url}{parameter_code}/date/{region_code}.txt"
        
        # Print for debugging
        print(f"Attempting to fetch data from: {url}")
        
        retries = 0
        last_exception = None
        
        while retries < self.max_retries:
            try:
                print(f"Fetching data from {url} (attempt {retries + 1}/{self.max_retries})")
                response = requests.get(url)
                
                # Print status code for debugging
                print(f"Response status code: {response.status_code}")
                
                # If it's a 404, we'll check if the response contains useful content anyway
                if response.status_code == 404:
                    print(f"Got 404 for {url}, but checking if response has content...")
                    if len(response.text) > 100:  # If it has substantial content
                        print(f"Response has content despite 404, proceeding with content...")
                        return response.text
                    else:
                        print(f"Response has no usable content. Content preview: {response.text[:100]}")
                
                response.raise_for_status()  # Raise an exception for HTTP errors
                
                # Print content preview for debugging
                content_preview = response.text[:200] + "..." if len(response.text) > 200 else response.text
                print(f"Successfully fetched data. Content preview: {content_preview}")
                
                return response.text
            except requests.RequestException as e:
                last_exception = e
                retries += 1
                print(f"Request failed: {str(e)}")
                if retries < self.max_retries:
                    wait_time = self.retry_delay * (2 ** (retries - 1))  # Exponential backoff
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"Failed to fetch data after {self.max_retries} attempts: {str(e)}")
        
        # If we get here, all retries failed
        if last_exception:
            raise last_exception
        
        # Fallback error in case no exception was captured
        raise requests.RequestException(f"Failed to fetch data from {url} after {self.max_retries} attempts")
    
    def parse_data(self, content: str) -> Tuple[Dict, List[Dict]]:
        """
        Parse the content of a MetOffice data file.
        
        Args:
            content: The text content of the file
            
        Returns:
            A tuple containing:
            - metadata: Dictionary with metadata about the dataset
            - data: List of dictionaries with the parsed data points
        """
        # Print for debugging
        print(f"Content length: {len(content)}")
        print(f"Content preview: {content[:500]}...")
        
        # Split the content into lines
        lines = content.strip().split('\n')
        print(f"Number of lines: {len(lines)}")
        
        # Extract metadata from the header
        metadata = self._parse_metadata(lines)
        print(f"Extracted metadata: {metadata}")
        
        # Find the line where data starts
        data_start_idx = 0
        for i, line in enumerate(lines):
            if re.match(r'^\s*year\s+jan\s+feb', line.lower()):
                data_start_idx = i + 1
                print(f"Found data start at line {i}: {line}")
                break
        
        if data_start_idx == 0:
            print("Could not find the start of data in the file. First 10 lines:")
            for i, line in enumerate(lines[:10]):
                print(f"Line {i}: {line}")
            raise ValueError("Could not find the start of data in the file")
        
        # Extract the data section
        data_lines = lines[data_start_idx:]
        print(f"Number of data lines: {len(data_lines)}")
        if data_lines:
            print(f"First data line: {data_lines[0]}")
            if len(data_lines) > 1:
                print(f"Second data line: {data_lines[1]}")
        
        # Process the data using pandas for better handling
        data = self._parse_data_with_pandas('\n'.join(data_lines))
        print(f"Number of parsed data records: {len(data)}")
        if data:
            print(f"First parsed record: {data[0]}")
        
        return metadata, data
    
    def _parse_metadata(self, lines: List[str]) -> Dict:
        """Extract metadata from the header lines."""
        metadata = {}
        
        # Print the header lines for debugging
        print("Header lines:")
        for i, line in enumerate(lines[:10]):
            print(f"Line {i}: {line}")
        
        # Look for metadata patterns in the header
        for line in lines[:10]:  # Assume metadata is within the first 10 lines
            # For MetOffice data, try to extract information from the header text
            if "monthly" in line.lower() or "daily" in line.lower():
                # This line likely contains parameter information
                if "temperature" in line.lower():
                    metadata['parameter_name'] = "Maximum Temperature"
                    metadata['unit'] = "°C"
                elif "rainfall" in line.lower():
                    metadata['parameter_name'] = "Rainfall"
                    metadata['unit'] = "mm"
                elif "sunshine" in line.lower():
                    metadata['parameter_name'] = "Sunshine"
                    metadata['unit'] = "hours"
            
            # Try to match region from the header
            if "uk" in line.lower():
                metadata['region_name'] = "United Kingdom"
            elif "england" in line.lower() and "wales" in line.lower():
                metadata['region_name'] = "England and Wales"
            elif "england" in line.lower():
                metadata['region_name'] = "England"
            elif "scotland" in line.lower():
                metadata['region_name'] = "Scotland"
            elif "wales" in line.lower():
                metadata['region_name'] = "Wales"
            elif "northern ireland" in line.lower() or "n ireland" in line.lower():
                metadata['region_name'] = "Northern Ireland"
        
        # If still not found, use traditional pattern matching
        if 'parameter_name' not in metadata or 'region_name' not in metadata:
            for line in lines[:10]:
                # Try to match parameter and region
                param_match = re.search(r'Parameter:\s*(.*?)(?:\s*\(|\s*$)', line)
                if param_match:
                    metadata['parameter_name'] = param_match.group(1).strip()
                
                # Match units if available
                unit_match = re.search(r'\((.*?)\)', line)
                if unit_match and 'parameter_name' in metadata:
                    metadata['unit'] = unit_match.group(1).strip()
                
                # Try to match region
                region_match = re.search(r'Region:\s*(.*?)(?:\s*\(|\s*$)', line)
                if region_match:
                    metadata['region_name'] = region_match.group(1).strip()
        
        print(f"Extracted metadata: {metadata}")
        return metadata
    
    def _parse_data_with_pandas(self, data_text: str) -> List[Dict]:
        """
        Parse the data section using pandas for better handling of the fixed-width format.
        
        Args:
            data_text: The text containing just the data rows
            
        Returns:
            List of dictionaries with the parsed data points
        """
        print(f"Data text preview to parse: '{data_text[:200]}'")
        
        try:
            # For MetOffice data, we need to handle the fixed format specially
            lines = data_text.strip().split('\n')
            
            # Define the expected column names for MetOffice data
            column_names = ['year', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 
                           'jul', 'aug', 'sep', 'oct', 'nov', 'dec', 'win', 
                           'spr', 'sum', 'aut', 'ann']
            
            print(f"Using column names: {column_names}")
            
            # Create a list to hold the processed rows
            rows = []
            
            # Process each line of data
            for line in lines:
                parts = line.strip().split()
                if len(parts) > 0 and parts[0].isdigit():  # Check if first item is a year
                    # Ensure we have enough columns
                    while len(parts) < len(column_names):
                        parts.append('---')  # Pad with missing value markers
                    
                    # Truncate if we have too many columns
                    if len(parts) > len(column_names):
                        parts = parts[:len(column_names)]
                    
                    rows.append(parts)
            
            # Create a DataFrame from the processed rows
            if rows:
                df = pd.DataFrame(rows, columns=column_names)
                
                # Convert to numeric values, coercing errors to NaN
                for col in df.columns:
                    if col != 'year':  # Skip the year column
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                
                print(f"DataFrame shape: {df.shape}")
                print("First 3 rows:")
                print(df.head(3))
                
                # Initialize our result list
                formatted_result = []
                
                # Process monthly data
                monthly_columns = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 
                                 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
                
                # Map month names to numbers
                month_map = {
                    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
                }
                
                # Process monthly data
                monthly_count = 0
                for _, row in df.iterrows():
                    year = int(row['year'])
                    for month in monthly_columns:
                        if pd.notna(row[month]):
                            formatted_result.append({
                                'year': year,
                                'period_type': 'monthly',
                                'month': month_map[month],
                                'value': float(row[month])
                            })
                            monthly_count += 1
                
                print(f"Processed {monthly_count} monthly records")
                
                # Process annual data if available
                annual_count = 0
                for _, row in df.iterrows():
                    if pd.notna(row['ann']):
                        formatted_result.append({
                            'year': int(row['year']),
                            'period_type': 'ann',
                            'month': None,
                            'value': float(row['ann'])
                        })
                        annual_count += 1
                
                print(f"Processed {annual_count} annual records")
                
                # Process seasonal data
                seasonal_columns = {'win': 'win', 'spr': 'spr', 'sum': 'sum', 'aut': 'aut'}
                seasonal_count = 0
                
                for season, code in seasonal_columns.items():
                    for _, row in df.iterrows():
                        if pd.notna(row[season]):
                            formatted_result.append({
                                'year': int(row['year']),
                                'period_type': code,
                                'month': None,
                                'value': float(row[season])
                            })
                            seasonal_count += 1
                
                print(f"Processed {seasonal_count} seasonal records")
                print(f"Total records processed: {len(formatted_result)}")
                return formatted_result
            else:
                print("No valid data rows found")
                return []
                
        except Exception as e:
            print(f"Error parsing data with pandas: {str(e)}")
            import traceback
            traceback.print_exc()
            # Return empty list on error
            return []
    
    def save_to_database(self, parameter_code: str, region_code: str, metadata: Dict, data: List[Dict]) -> int:
        """
        Save the parsed data to the database.
        
        Args:
            parameter_code: The code for the parameter
            region_code: The code for the region
            metadata: Dictionary with metadata about the dataset
            data: List of dictionaries with the parsed data points
            
        Returns:
            The number of records saved
        """
        # Get or create the region
        region, _ = Region.objects.get_or_create(
            code=region_code,
            defaults={'name': metadata.get('region_name', region_code)}
        )
        
        # Get or create the parameter
        parameter, _ = Parameter.objects.get_or_create(
            code=parameter_code,
            defaults={
                'name': metadata.get('parameter_name', parameter_code),
                'unit': metadata.get('unit', '')
            }
        )
        
        # Count records by type for reporting
        monthly_count = 0
        annual_count = 0
        seasonal_count = 0
        
        # Create or update the weather data records
        for item in data:
            # Create or update this record
            weather_data, created = WeatherData.objects.update_or_create(
                region=region,
                parameter=parameter,
                year=item['year'],
                period_type=item['period_type'],
                month=item['month'],
                defaults={'value': item['value']}
            )
            
            # Count by type
            if item['period_type'] == 'monthly':
                monthly_count += 1
            elif item['period_type'] == 'ann':
                annual_count += 1
            else:
                seasonal_count += 1
        
        # Return total count
        total_count = monthly_count + annual_count + seasonal_count
        print(f"Successfully imported {total_count} records for {parameter_code} in {region_code} ({monthly_count} monthly, {annual_count} annual, {seasonal_count} seasonal)")
        
        return total_count