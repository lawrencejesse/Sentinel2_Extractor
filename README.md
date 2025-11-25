# Geospatial Analysis Platform for Oilfield Reclamation Assessment

## Overview

A comprehensive Python-based geospatial analysis platform using Google Earth Engine for satellite imagery analysis and oilfield reclamation assessment. The platform combines multiple data sources including AlphaEarth Foundation embeddings, AAFC crop inventories, ERA-5 Land precipitation data, and Sentinel-2 imagery to provide robust environmental monitoring and land capability assessment.

## Key Features

### Core Analysis Capabilities
- **Reclamation Site Assessment**: Quantitative evaluation of oilfield lease recovery using 64D embeddings
- **Precipitation Context Analysis**: ERA-5 Land integration for weather impact assessment
- **Multi-Year Productivity Tracking**: Temporal analysis of vegetation health trends
- **Statistical Anomaly Detection**: Robust z-score analysis using Median Absolute Deviation
- **Crop Type Identification**: Automated extraction from AAFC Annual Crop Inventory
- **Difference-in-Differences Analysis**: Compare lease performance against regional references

### Data Sources
- **Google Earth Engine Collections**:
  - AlphaEarth Foundation: 64D embeddings at 10m resolution
  - AAFC Annual Crop Inventory: Crop classification 2009-2023 at 30m resolution
  - ERA-5 Land Monthly: Precipitation data at 11km resolution
  - Sentinel-2 MSI: Multispectral imagery for NDVI/NDMI analysis

## Project Structure

### Analysis Notebooks
- `Reclamation_Analysis_AEFv4.ipynb` - **RECOMMENDED** Latest version with all fixes for AEF band naming and edge handling
- `Reclamation_Analysis_AEFv2.ipynb` - Previous version with DiD analysis
- `Reclamation_Analysis_AEF.ipynb` - Original implementation with regional references
- `Precipitation_Context_Analysis.ipynb` - ERA-5 precipitation analysis and anomaly detection
- `Reclamation_Assessment_Robust_Z_Score.ipynb` - Statistical anomaly detection
- `Sentinel2_RasterExtractor.ipynb` - Sentinel-2 imagery extraction
- `Multi_Year_ProductivityRaster.ipynb` - Multi-year NDVI productivity analysis
- `NDVI_Mean_and_St_Dev_Bell_Curve_V1.ipynb` - NDVI statistical analysis

### Python Modules
- `precipitation_analysis.py` - ERA-5 precipitation extraction and analysis
- `integrate_precipitation.py` - Integration utilities for precipitation context

## Getting Started

### Prerequisites
- Python 3.11+
- Google Earth Engine account and authentication
- JupyterLab environment

### Installation

1. Install required packages:
   ```bash
   uv pip install -r pyproject.toml
   ```

2. Authenticate with Google Earth Engine:
   ```python
   import ee
   ee.Authenticate()
   ee.Initialize(project="your-project-id")
   ```

3. Launch JupyterLab:
   ```bash
   jupyter lab --port=5000 --ip=0.0.0.0
   ```

## Analysis Workflows

### 1. Basic Reclamation Assessment

Start with `Reclamation_Analysis_AEFv2.ipynb`:
- Upload field boundary (KML/GeoJSON/SHP)
- Upload lease boundary polygon
- Automatic crop type extraction
- Compare lease vs background field performance
- Generate recovery trajectory visualization

### 2. Precipitation Context Analysis

Use `Precipitation_Context_Analysis.ipynb`:
- Extract ERA-5 Land precipitation data
- Calculate 10-year baseline statistics (2010-2019)
- Classify conditions (Extremely Dry to Extremely Wet)
- Generate monthly and seasonal anomaly reports

### 3. Integrated Analysis

Combine reclamation and precipitation data:
```python
from integrate_precipitation import integrate_precipitation_with_notebook

# Run after completing reclamation analysis
enhanced_results = integrate_precipitation_with_notebook(results_df)
```

## Methodology

### Difference-in-Differences (DiD) Approach

The platform uses a DiD methodology to assess reclamation success:

```
DiD Score = (Lease vs Regional) - (Background vs Regional)
```

**Interpretation**:
- DiD ≈ 0 (±0.05): Lease performing equivalently → **Reclamation Success**
- DiD < -0.05: Lease underperforming → **Needs Attention**
- DiD > 0.05: Lease outperforming (investigate for artifacts)

### Precipitation Adjustment

The analysis accounts for weather impacts:
- **Dry years** (< -15% anomaly): Tolerance added for underperformance
- **Normal years** (±15% anomaly): Baseline expectations
- **Wet years** (> +15% anomaly): Higher performance expected

## Output Products

### Generated Files
- `reclamation_analysis_results.csv`: Time series of performance metrics
- `precipitation_context.json`: Weather anomaly data
- `enhanced_reclamation_results.csv`: Integrated analysis with weather adjustment
- `integrated_analysis.png`: Combined visualization
- `enhanced_summary.txt`: Comprehensive assessment report

### Visualizations
1. **Recovery Trajectory**: Cosine similarity trends over time
2. **Precipitation Overlay**: Performance metrics with weather context
3. **Anomaly Charts**: Monthly and seasonal precipitation deviations
4. **Summary Tables**: Year-by-year classification and metrics

## Recent Updates

### November 2024
- **NEW**: v4 notebook with comprehensive fixes for AlphaEarth extraction
  - Fixed band naming consistently (A00-A63 format)
  - Uses `selfMask()` to automatically exclude null/masked pixels at edges
  - Returns explicit failure states that the analysis loop skips (no zero-vector contamination)
  - Minimum pixel count validation (10+ valid pixels required)
  - Robust lease vs field comparison with proper error handling
- **NEW**: ERA-5 Land precipitation integration for weather context
- **NEW**: Precipitation anomaly classification and adjustment algorithms
- **NEW**: Integrated visualization combining performance and weather
- **NEW**: Enhanced summary reports with weather-adjusted metrics
- Fixed AlphaEarth band naming issue (embedding_0 → A00)
- Added simplified analysis option (v2 notebook)
- Implemented smart fallback for insufficient regional samples

## Troubleshooting

### Common Issues

1. **"Band pattern 'embedding_0' did not match any bands"**
   - Solution: Use `Reclamation_Analysis_AEFv4.ipynb` which has correct 'A00-A63' format
   - If using older notebooks, restart kernel after updating band references

2. **"No valid crop code found"**
   - Solution: Increase sample_size parameter or check boundary overlap with AAFC data

3. **"Insufficient regional samples"**
   - Solution: System will automatically expand search radius (smart fallback)

4. **Precipitation data not loading**
   - Solution: Ensure ERA-5 Land collection access in GEE project

## Dependencies

### Core Libraries
- **Geospatial**: earthengine-api, geemap, geopandas, rasterio, fiona, shapely
- **Data Analysis**: numpy, pandas, scipy
- **Visualization**: matplotlib, ipywidgets
- **Notebook Environment**: jupyterlab, notebook

---

*Built with Google Earth Engine, AlphaEarth Foundation, and open-source geospatial tools*
