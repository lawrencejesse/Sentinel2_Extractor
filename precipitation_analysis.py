"""
ERA-5 Land Precipitation Analysis Module for Reclamation Assessment
This module provides functions to extract and analyze precipitation data from ERA-5 Land
to provide context for vegetation trends and reclamation monitoring.
"""

import ee
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional, Union
from datetime import datetime, timedelta
import calendar

class PrecipitationAnalyzer:
    """
    Analyze precipitation patterns using ERA-5 Land data from Google Earth Engine.
    Provides monthly and seasonal precipitation statistics and anomaly detection.
    """
    
    def __init__(self, geometry: ee.Geometry, baseline_years: range = range(2010, 2020)):
        """
        Initialize the precipitation analyzer.
        
        Parameters:
        -----------
        geometry : ee.Geometry
            The area of interest for precipitation analysis
        baseline_years : range
            Years to use as baseline for calculating normal precipitation (default: 2010-2019)
        """
        self.geometry = geometry
        self.baseline_years = baseline_years
        self.era5_collection = 'ECMWF/ERA5_LAND/MONTHLY_AGGR'
        
    def extract_monthly_precipitation(self, year: int, months: List[int] = None) -> Dict:
        """
        Extract monthly precipitation totals from ERA-5 Land data.
        
        Parameters:
        -----------
        year : int
            Year to extract data for
        months : List[int], optional
            Specific months to extract (1-12). Default is April-October (growing season)
            
        Returns:
        --------
        Dict containing monthly precipitation values and metadata
        """
        if months is None:
            months = list(range(4, 11))  # April to October (growing season)
        
        monthly_data = {}
        
        for month in months:
            # Define date range for the month
            start_date = f'{year}-{month:02d}-01'
            # Get last day of month
            last_day = calendar.monthrange(year, month)[1]
            end_date = f'{year}-{month:02d}-{last_day}'
            
            # Load ERA5-Land monthly aggregated data
            era5_collection = ee.ImageCollection(self.era5_collection).filter(
                ee.Filter.date(start_date, end_date)
            )
            
            # Check if collection has any images
            collection_size = era5_collection.size()
            
            if collection_size.getInfo() > 0:
                era5 = era5_collection.first()
                # Extract total precipitation (m to mm conversion: multiply by 1000)
                precip = era5.select('total_precipitation_sum').multiply(1000)
                
                # Calculate mean precipitation over the geometry
                stats = precip.reduceRegion(
                    reducer=ee.Reducer.mean(),
                    geometry=self.geometry,
                    scale=11132,  # ERA5-Land native resolution (~11km)
                    maxPixels=1e9
                )
                
                precip_mm = stats.get('total_precipitation_sum').getInfo()
                monthly_data[month] = {
                    'precipitation_mm': precip_mm,
                    'month_name': calendar.month_name[month],
                    'year': year
                }
            else:
                print(f"Warning: No ERA5 data found for {year}-{month:02d}")
                monthly_data[month] = {
                    'precipitation_mm': None,
                    'month_name': calendar.month_name[month],
                    'year': year
                }
        
        return monthly_data
    
    def calculate_baseline_statistics(self) -> Dict:
        """
        Calculate baseline precipitation statistics for the normal period.
        
        Returns:
        --------
        Dict containing monthly means, stdev, and percentiles
        """
        baseline_data = {month: [] for month in range(4, 11)}
        
        print(f"Calculating baseline precipitation statistics ({self.baseline_years.start}-{self.baseline_years.stop-1})...")
        
        for year in self.baseline_years:
            year_data = self.extract_monthly_precipitation(year)
            for month, values in year_data.items():
                if values['precipitation_mm'] is not None:
                    baseline_data[month].append(values['precipitation_mm'])
        
        # Calculate statistics
        baseline_stats = {}
        for month, precip_values in baseline_data.items():
            if len(precip_values) > 0:
                precip_array = np.array(precip_values)
                baseline_stats[month] = {
                    'mean': np.mean(precip_array),
                    'median': np.median(precip_array),
                    'stdev': np.std(precip_array),
                    'p10': np.percentile(precip_array, 10),
                    'p25': np.percentile(precip_array, 25),
                    'p75': np.percentile(precip_array, 75),
                    'p90': np.percentile(precip_array, 90),
                    'month_name': calendar.month_name[month]
                }
            else:
                print(f"Warning: No valid precipitation data for month {month} in baseline period")
                baseline_stats[month] = {
                    'mean': 0,
                    'median': 0,
                    'stdev': 0,
                    'p10': 0,
                    'p25': 0,
                    'p75': 0,
                    'p90': 0,
                    'month_name': calendar.month_name[month]
                }
        
        return baseline_stats
    
    def classify_precipitation_anomaly(self, current_precip: float, baseline_stats: Dict) -> str:
        """
        Classify current precipitation relative to baseline.
        
        Parameters:
        -----------
        current_precip : float
            Current precipitation value in mm
        baseline_stats : Dict
            Baseline statistics for comparison
            
        Returns:
        --------
        Classification string: 'Extremely Dry', 'Dry', 'Normal', 'Wet', 'Extremely Wet'
        """
        if current_precip <= baseline_stats['p10']:
            return 'Extremely Dry'
        elif current_precip <= baseline_stats['p25']:
            return 'Dry'
        elif current_precip <= baseline_stats['p75']:
            return 'Normal'
        elif current_precip <= baseline_stats['p90']:
            return 'Wet'
        else:
            return 'Extremely Wet'
    
    def analyze_growing_season(self, year: int, baseline_stats: Dict = None) -> pd.DataFrame:
        """
        Analyze precipitation for a growing season with anomaly classification.
        
        Parameters:
        -----------
        year : int
            Year to analyze
        baseline_stats : Dict, optional
            Pre-calculated baseline statistics. If None, will calculate.
            
        Returns:
        --------
        DataFrame with monthly precipitation analysis
        """
        if baseline_stats is None:
            baseline_stats = self.calculate_baseline_statistics()
        
        current_data = self.extract_monthly_precipitation(year)
        
        results = []
        for month in range(4, 11):
            if month in current_data and month in baseline_stats:
                current_precip = current_data[month]['precipitation_mm']
                baseline = baseline_stats[month]
                
                if current_precip is not None and baseline['mean'] > 0:
                    anomaly = current_precip - baseline['mean']
                    anomaly_percent = (anomaly / baseline['mean']) * 100
                    classification = self.classify_precipitation_anomaly(current_precip, baseline)
                    
                    results.append({
                        'Month': baseline['month_name'],
                        'Precipitation (mm)': round(current_precip, 1),
                        'Normal (mm)': round(baseline['mean'], 1),
                        'Anomaly (mm)': round(anomaly, 1),
                        'Anomaly (%)': round(anomaly_percent, 1),
                        'Classification': classification
                    })
                else:
                    # Handle missing data
                    results.append({
                        'Month': baseline['month_name'],
                        'Precipitation (mm)': 0,
                        'Normal (mm)': round(baseline['mean'], 1) if baseline['mean'] > 0 else 0,
                        'Anomaly (mm)': 0,
                        'Anomaly (%)': 0,
                        'Classification': 'No Data'
                    })
        
        # Add seasonal summary
        season_precip = sum(r['Precipitation (mm)'] for r in results if r['Classification'] != 'No Data')
        season_normal = sum(r['Normal (mm)'] for r in results if r['Classification'] != 'No Data')
        
        if season_normal > 0:
            season_anomaly = season_precip - season_normal
            season_anomaly_percent = (season_anomaly / season_normal) * 100
        else:
            season_anomaly = 0
            season_anomaly_percent = 0
        
        results.append({
            'Month': 'SEASONAL TOTAL',
            'Precipitation (mm)': round(season_precip, 1),
            'Normal (mm)': round(season_normal, 1),
            'Anomaly (mm)': round(season_anomaly, 1),
            'Anomaly (%)': round(season_anomaly_percent, 1),
            'Classification': self._classify_seasonal_anomaly(season_anomaly_percent)
        })
        
        return pd.DataFrame(results)
    
    def _classify_seasonal_anomaly(self, anomaly_percent: float) -> str:
        """
        Classify seasonal precipitation anomaly.
        
        Parameters:
        -----------
        anomaly_percent : float
            Seasonal anomaly as percentage of normal
            
        Returns:
        --------
        Classification string
        """
        if anomaly_percent <= -30:
            return 'Extremely Dry Season'
        elif anomaly_percent <= -15:
            return 'Dry Season'
        elif anomaly_percent <= 15:
            return 'Normal Season'
        elif anomaly_percent <= 30:
            return 'Wet Season'
        else:
            return 'Extremely Wet Season'
    
    def plot_precipitation_analysis(self, year: int, baseline_stats: Dict = None, 
                                   save_path: str = None) -> None:
        """
        Create visualization of precipitation analysis.
        
        Parameters:
        -----------
        year : int
            Year to analyze and plot
        baseline_stats : Dict, optional
            Pre-calculated baseline statistics
        save_path : str, optional
            Path to save the figure
        """
        if baseline_stats is None:
            baseline_stats = self.calculate_baseline_statistics()
        
        df = self.analyze_growing_season(year, baseline_stats)
        monthly_df = df[df['Month'] != 'SEASONAL TOTAL']
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Precipitation Analysis for {year} Growing Season', fontsize=16, fontweight='bold')
        
        # 1. Monthly precipitation comparison
        ax1 = axes[0, 0]
        months = monthly_df['Month'].values
        x = np.arange(len(months))
        width = 0.35
        
        bars1 = ax1.bar(x - width/2, monthly_df['Precipitation (mm)'], width, label=f'{year}', color='steelblue')
        bars2 = ax1.bar(x + width/2, monthly_df['Normal (mm)'], width, label='Normal (2010-2019)', color='gray', alpha=0.6)
        
        ax1.set_xlabel('Month')
        ax1.set_ylabel('Precipitation (mm)')
        ax1.set_title('Monthly Precipitation vs Normal')
        ax1.set_xticks(x)
        ax1.set_xticklabels(months, rotation=45)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax1.annotate(f'{height:.0f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8)
        
        # 2. Anomaly chart
        ax2 = axes[0, 1]
        colors = ['red' if a < 0 else 'green' for a in monthly_df['Anomaly (mm)']]
        bars = ax2.bar(months, monthly_df['Anomaly (mm)'], color=colors, alpha=0.7)
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax2.set_xlabel('Month')
        ax2.set_ylabel('Anomaly (mm)')
        ax2.set_title('Precipitation Anomaly from Normal')
        ax2.set_xticklabels(months, rotation=45)
        ax2.grid(True, alpha=0.3)
        
        # 3. Classification pie chart
        ax3 = axes[1, 0]
        classification_counts = monthly_df['Classification'].value_counts()
        colors_map = {
            'Extremely Dry': '#8B0000',
            'Dry': '#FFA500',
            'Normal': '#228B22',
            'Wet': '#4682B4',
            'Extremely Wet': '#000080'
        }
        pie_colors = [colors_map.get(c, 'gray') for c in classification_counts.index]
        ax3.pie(classification_counts.values, labels=classification_counts.index, autopct='%1.0f%%',
                colors=pie_colors, startangle=90)
        ax3.set_title('Monthly Classification Distribution')
        
        # 4. Summary statistics text
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        season_row = df[df['Month'] == 'SEASONAL TOTAL'].iloc[0]
        summary_text = f"""
        GROWING SEASON SUMMARY ({year})
        
        Total Precipitation: {season_row['Precipitation (mm)']} mm
        Normal Precipitation: {season_row['Normal (mm)']} mm
        Anomaly: {season_row['Anomaly (mm)']} mm ({season_row['Anomaly (%)']:.1f}%)
        
        Classification: {season_row['Classification']}
        
        Implications for Vegetation:
        • {'Drought stress likely affecting crop growth' if season_row['Anomaly (%)'] < -15 else ''}
        • {'Normal moisture conditions for typical growth' if -15 <= season_row['Anomaly (%)'] <= 15 else ''}
        • {'Excess moisture may affect crop quality' if season_row['Anomaly (%)'] > 30 else ''}
        • {'Good moisture availability for growth' if 15 < season_row['Anomaly (%)'] <= 30 else ''}
        """
        
        ax4.text(0.1, 0.5, summary_text, fontsize=11, verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Figure saved to {save_path}")
        
        plt.show()
    
    def compare_multiple_years(self, years: List[int], baseline_stats: Dict = None) -> pd.DataFrame:
        """
        Compare precipitation across multiple years.
        
        Parameters:
        -----------
        years : List[int]
            Years to compare
        baseline_stats : Dict, optional
            Pre-calculated baseline statistics
            
        Returns:
        --------
        DataFrame with multi-year comparison
        """
        if baseline_stats is None:
            baseline_stats = self.calculate_baseline_statistics()
        
        results = []
        for year in years:
            df = self.analyze_growing_season(year, baseline_stats)
            season_row = df[df['Month'] == 'SEASONAL TOTAL'].iloc[0]
            results.append({
                'Year': year,
                'Total Precip (mm)': season_row['Precipitation (mm)'],
                'Normal (mm)': season_row['Normal (mm)'],
                'Anomaly (%)': season_row['Anomaly (%)'],
                'Classification': season_row['Classification']
            })
        
        return pd.DataFrame(results)