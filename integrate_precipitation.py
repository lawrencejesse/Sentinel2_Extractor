"""
Integration module to add precipitation context to reclamation analysis.
This module enhances the existing analysis with weather context.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Optional
import json

def add_precipitation_context_to_results(results_df: pd.DataFrame, 
                                        precipitation_file: str = 'output_data/precipitation_context.json') -> pd.DataFrame:
    """
    Add precipitation context columns to existing reclamation analysis results.
    
    Parameters:
    -----------
    results_df : pd.DataFrame
        Existing results from reclamation analysis with columns like 'year', 'crop', 'lease_vs_regional', etc.
    precipitation_file : str
        Path to precipitation context JSON file
        
    Returns:
    --------
    Enhanced DataFrame with precipitation context columns
    """
    # Load precipitation context
    with open(precipitation_file, 'r') as f:
        precip_data = json.load(f)
    
    # Add precipitation columns to results
    results_df['precip_anomaly_pct'] = 0.0
    results_df['precip_classification'] = ''
    results_df['precip_impact'] = ''
    results_df['adjusted_performance'] = 0.0
    
    for idx, row in results_df.iterrows():
        year = row['year']
        if str(year) in precip_data['yearly_analysis']:
            year_data = precip_data['yearly_analysis'][str(year)]
            results_df.at[idx, 'precip_anomaly_pct'] = year_data['anomaly_percent']
            results_df.at[idx, 'precip_classification'] = year_data['classification']
            results_df.at[idx, 'precip_impact'] = year_data['vegetation_impact']
            
            # Calculate adjusted performance (normalize for precipitation effects)
            # If it's a dry year, we expect lower performance
            # If it's a wet year, we might expect better performance
            adjustment_factor = 0.0
            if year_data['anomaly_percent'] < -15:  # Dry year
                adjustment_factor = 0.05  # Add tolerance for underperformance
            elif year_data['anomaly_percent'] > 15:  # Wet year
                adjustment_factor = -0.03  # Expect better performance
            
            if 'difference_in_differences' in results_df.columns:
                results_df.at[idx, 'adjusted_performance'] = row['difference_in_differences'] + adjustment_factor
    
    return results_df

def create_integrated_visualization(results_df: pd.DataFrame, 
                                   save_path: str = 'output_data/integrated_analysis.png') -> None:
    """
    Create visualization combining reclamation metrics with precipitation context.
    
    Parameters:
    -----------
    results_df : pd.DataFrame
        Results DataFrame with precipitation context
    save_path : str
        Path to save the figure
    """
    fig, axes = plt.subplots(3, 1, figsize=(14, 12))
    
    # Plot 1: Cosine similarity with precipitation overlay
    ax1 = axes[0]
    ax1_twin = ax1.twinx()
    
    # Plot similarity metrics
    if 'lease_vs_regional' in results_df.columns:
        ax1.plot(results_df['year'], results_df['lease_vs_regional'], 
                marker='o', linewidth=2, label='Lease vs Regional', color='red')
        ax1.plot(results_df['year'], results_df['background_vs_regional'], 
                marker='s', linewidth=2, label='Background vs Regional', color='green')
    elif 'lease_vs_background' in results_df.columns:
        ax1.plot(results_df['year'], results_df['lease_vs_background'], 
                marker='o', linewidth=2, label='Lease vs Background', color='blue')
    
    # Overlay precipitation anomaly
    colors = ['brown' if a < 0 else 'lightblue' for a in results_df['precip_anomaly_pct']]
    ax1_twin.bar(results_df['year'], results_df['precip_anomaly_pct'], 
                alpha=0.3, color=colors, width=0.6)
    
    ax1.set_xlabel('Year', fontsize=12)
    ax1.set_ylabel('Cosine Similarity', fontsize=12)
    ax1_twin.set_ylabel('Precipitation Anomaly (%)', fontsize=12)
    ax1.set_title('Reclamation Performance with Precipitation Context', 
                 fontsize=14, fontweight='bold')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    ax1_twin.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    
    # Add precipitation classification labels
    for idx, row in results_df.iterrows():
        if row['precip_classification']:
            ax1.text(row['year'], 0.05, row['precip_classification'].split()[0], 
                    rotation=90, fontsize=8, ha='center', alpha=0.7)
    
    # Plot 2: Adjusted vs Raw Performance
    if 'difference_in_differences' in results_df.columns:
        ax2 = axes[1]
        
        # Raw performance
        ax2.plot(results_df['year'], results_df['difference_in_differences'], 
                marker='o', linewidth=2, label='Raw Performance (DiD)', color='blue')
        
        # Adjusted performance
        ax2.plot(results_df['year'], results_df['adjusted_performance'], 
                marker='^', linewidth=2, label='Precipitation-Adjusted Performance', 
                color='purple', linestyle='--')
        
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
        ax2.axhline(y=-0.05, color='red', linestyle='--', alpha=0.5)
        
        ax2.set_xlabel('Year', fontsize=12)
        ax2.set_ylabel('Performance Score', fontsize=12)
        ax2.set_title('Raw vs Precipitation-Adjusted Performance', 
                     fontsize=14, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
    
    # Plot 3: Summary table
    ax3 = axes[2]
    ax3.axis('tight')
    ax3.axis('off')
    
    # Create summary data
    summary_data = []
    for _, row in results_df.iterrows():
        if 'difference_in_differences' in results_df.columns:
            perf_val = row['difference_in_differences']
            adj_perf = row['adjusted_performance']
        else:
            perf_val = row.get('lease_vs_background', 0)
            adj_perf = perf_val
            
        summary_data.append([
            int(row['year']),
            row.get('crop', 'N/A')[:15],
            row['precip_classification'].split()[0] if row['precip_classification'] else 'N/A',
            f"{row['precip_anomaly_pct']:.0f}%",
            f"{perf_val:.3f}",
            f"{adj_perf:.3f}"
        ])
    
    # Create table
    table = ax3.table(cellText=summary_data,
                     colLabels=['Year', 'Crop', 'Precip', 'Anomaly', 'Raw Perf', 'Adj Perf'],
                     cellLoc='center',
                     loc='center',
                     colColours=['lightgray']*6)
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)
    
    # Color code the precipitation cells
    for i, row_data in enumerate(summary_data, 1):
        precip_class = row_data[2]
        if 'Dry' in precip_class:
            table[(i, 2)].set_facecolor('#ffcccc')
        elif 'Wet' in precip_class:
            table[(i, 2)].set_facecolor('#ccccff')
        else:
            table[(i, 2)].set_facecolor('#ccffcc')
    
    ax3.set_title('Summary Table with Precipitation Context', 
                 fontsize=12, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"✓ Integrated visualization saved to {save_path}")

def generate_enhanced_summary(results_df: pd.DataFrame) -> str:
    """
    Generate an enhanced summary report including precipitation context.
    
    Parameters:
    -----------
    results_df : pd.DataFrame
        Results DataFrame with precipitation context
        
    Returns:
    --------
    String containing the enhanced summary report
    """
    # Calculate statistics
    dry_years = results_df[results_df['precip_anomaly_pct'] < -15]
    wet_years = results_df[results_df['precip_anomaly_pct'] > 15]
    normal_years = results_df[(results_df['precip_anomaly_pct'] >= -15) & 
                             (results_df['precip_anomaly_pct'] <= 15)]
    
    summary = f"""
    ENHANCED RECLAMATION ASSESSMENT WITH PRECIPITATION CONTEXT
    ==========================================================
    
    Analysis Period: {results_df['year'].min()} - {results_df['year'].max()}
    Total Years Analyzed: {len(results_df)}
    
    PRECIPITATION CONTEXT:
    ----------------------
    Dry Years ({len(dry_years)}): {', '.join(map(str, dry_years['year'].values))}
    Normal Years ({len(normal_years)}): {', '.join(map(str, normal_years['year'].values))}
    Wet Years ({len(wet_years)}): {', '.join(map(str, wet_years['year'].values))}
    
    Average Precipitation Anomaly: {results_df['precip_anomaly_pct'].mean():.1f}%
    """
    
    if 'difference_in_differences' in results_df.columns:
        summary += f"""
    PERFORMANCE METRICS:
    --------------------
    Raw Performance (DiD):
      Mean: {results_df['difference_in_differences'].mean():.4f}
      Dry Years Mean: {dry_years['difference_in_differences'].mean():.4f if len(dry_years) > 0 else 'N/A'}
      Normal Years Mean: {normal_years['difference_in_differences'].mean():.4f if len(normal_years) > 0 else 'N/A'}
      Wet Years Mean: {wet_years['difference_in_differences'].mean():.4f if len(wet_years) > 0 else 'N/A'}
    
    Adjusted Performance:
      Mean: {results_df['adjusted_performance'].mean():.4f}
      Improvement from adjustment: {(results_df['adjusted_performance'] - results_df['difference_in_differences']).mean():.4f}
    
    INTERPRETATION:
    ---------------
    """
        
        # Determine overall assessment
        adj_mean = results_df['adjusted_performance'].mean()
        if adj_mean >= -0.05:
            summary += """
    ✓ ADJUSTED ASSESSMENT: When accounting for precipitation variability, 
      the lease site is performing equivalently to the background field.
      This suggests successful reclamation with equivalent land capability."""
        else:
            summary += f"""
    ⚠ ADJUSTED ASSESSMENT: Even after accounting for precipitation effects,
      the lease site is underperforming by {abs(adj_mean):.3f} on average.
      This suggests that factors beyond weather are limiting recovery."""
            
        # Add specific year insights
        if len(dry_years) > 0:
            summary += f"""
    
    DRY YEAR INSIGHTS:
    During dry years, the lease showed {'better' if dry_years['adjusted_performance'].mean() > dry_years['difference_in_differences'].mean() else 'worse'} 
    relative performance after precipitation adjustment, suggesting the site is 
    {'resilient to' if dry_years['adjusted_performance'].mean() > -0.05 else 'vulnerable to'} drought stress."""
    
    else:  # Simpler analysis without DiD
        summary += f"""
    PERFORMANCE METRICS:
    --------------------
    Mean Similarity: {results_df.get('lease_vs_background', results_df.get('lease_vs_regional', pd.Series())).mean():.4f}
    
    INTERPRETATION:
    ---------------
    Precipitation context helps explain year-to-year variations in performance.
    Dry years typically show lower vegetation productivity across all fields.
    """
    
    summary += """
    
    RECOMMENDATIONS:
    ----------------
    1. Focus additional assessment on normal precipitation years for most accurate evaluation
    2. Consider multi-year trends rather than single-year snapshots
    3. Account for lag effects - recovery may be delayed after extreme weather years
    4. Use precipitation-adjusted metrics for regulatory compliance decisions
    """
    
    return summary

# Helper function to be called from notebooks
def integrate_precipitation_with_notebook(results_df: pd.DataFrame, 
                                         output_dir: str = 'output_data') -> pd.DataFrame:
    """
    Main integration function to be called from existing notebooks.
    
    Parameters:
    -----------
    results_df : pd.DataFrame
        Results from your existing reclamation analysis
    output_dir : str
        Directory for output files
        
    Returns:
    --------
    Enhanced DataFrame with precipitation context
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if precipitation context exists
    precip_file = f'{output_dir}/precipitation_context.json'
    if not os.path.exists(precip_file):
        print("⚠ Warning: precipitation_context.json not found.")
        print("  Please run Precipitation_Context_Analysis.ipynb first to generate precipitation data.")
        return results_df
    
    # Add precipitation context
    print("Adding precipitation context to results...")
    enhanced_df = add_precipitation_context_to_results(results_df, precip_file)
    
    # Create visualizations
    print("Creating integrated visualizations...")
    create_integrated_visualization(enhanced_df, f'{output_dir}/integrated_analysis.png')
    
    # Generate summary
    print("Generating enhanced summary report...")
    summary = generate_enhanced_summary(enhanced_df)
    print(summary)
    
    # Save enhanced results
    enhanced_df.to_csv(f'{output_dir}/enhanced_reclamation_results.csv', index=False)
    with open(f'{output_dir}/enhanced_summary.txt', 'w') as f:
        f.write(summary)
    
    print(f"\n✓ Enhanced results saved to {output_dir}/")
    
    return enhanced_df