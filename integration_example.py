"""
Example code to add precipitation context to your existing Reclamation_Analysis_AEFv2.ipynb

Add this code cell after your reclamation analysis is complete to integrate precipitation context.
"""

# Example integration code to add to your notebook:

# After running your reclamation analysis and getting results_df, add:

# Cell 1: Import precipitation integration module
from integrate_precipitation import integrate_precipitation_with_notebook

# Cell 2: Run precipitation analysis (if not already done)
# First run the Precipitation_Context_Analysis.ipynb notebook to generate precipitation data
# This will create output_data/precipitation_context.json

# Cell 3: Integrate precipitation context with your results
if 'results_df' in locals() and len(results_df) > 0:
    print("Integrating precipitation context with reclamation analysis...")
    
    # Add precipitation context and create enhanced visualizations
    enhanced_results = integrate_precipitation_with_notebook(
        results_df, 
        output_dir='output_data'
    )
    
    # The function will:
    # 1. Add precipitation columns to your results
    # 2. Create integrated visualizations 
    # 3. Generate enhanced summary report
    # 4. Save all outputs to output_data/
    
    print("\n✓ Precipitation context successfully integrated!")
    print("Check output_data/ folder for:")
    print("  - integrated_analysis.png (combined visualization)")
    print("  - enhanced_reclamation_results.csv (results with weather context)")
    print("  - enhanced_summary.txt (comprehensive report)")
    
    # View the enhanced results
    display(enhanced_results[['year', 'crop', 'difference_in_differences', 
                             'precip_classification', 'precip_anomaly_pct', 
                             'adjusted_performance']])
else:
    print("Please run the reclamation analysis first to generate results_df")

# Cell 4: Quick interpretation helper
def interpret_with_precipitation(enhanced_results):
    """
    Helper function to interpret results with precipitation context
    """
    for _, row in enhanced_results.iterrows():
        year = row['year']
        crop = row.get('crop', 'Unknown')
        raw_perf = row.get('difference_in_differences', 0)
        adj_perf = row.get('adjusted_performance', 0)
        precip_class = row.get('precip_classification', 'Unknown')
        
        print(f"\n{year} - {crop}:")
        print(f"  Precipitation: {precip_class}")
        print(f"  Raw Performance: {raw_perf:.3f}")
        print(f"  Adjusted Performance: {adj_perf:.3f}")
        
        if precip_class in ['Extremely Dry Season', 'Dry Season']:
            if adj_perf > raw_perf:
                print(f"  → Performance adjusted UP due to drought conditions")
        elif precip_class in ['Extremely Wet Season', 'Wet Season']:
            if adj_perf < raw_perf:
                print(f"  → Performance adjusted DOWN (higher expectations in wet year)")
        
        if adj_perf >= -0.05:
            print(f"  ✓ Adjusted assessment: Performing equivalently")
        else:
            print(f"  ⚠ Adjusted assessment: Underperforming by {abs(adj_perf):.3f}")

# Run the interpretation
if 'enhanced_results' in locals():
    interpret_with_precipitation(enhanced_results)