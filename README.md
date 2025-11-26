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
| Notebook | Description |
|----------|-------------|
| `Reclamation_Analysis_AEFv4_working.ipynb` | **RECOMMENDED** - Latest version with all fixes for AEF band naming and edge handling using selfMask() |
| `Reclamation_Assessment_Robust_Z_Score.ipynb` | Robust z-score analysis for lease vs background comparison using MAD statistics |
| `Reclamation_Assessment_Z_Score_Enhanced.ipynb` | Extended z-score analysis with additional features |
| `Background_Data_Extraction.ipynb` | Self-contained notebook for extracting AAFC crop history and ERA-5 precipitation data |
| `Precipitation_Context_Analysis.ipynb` | ERA-5 precipitation analysis and anomaly detection |
| `Sentinel2_RasterExtractor.ipynb` | Extract Sentinel-2 imagery (NDVI, NDMI, RGB) from Google Earth Engine |
| `Multi_Year_ProductivityRaster.ipynb` | Multi-year NDVI productivity analysis |
| `NDVI_Mean_and_St_Dev_Bell_Curve_V1.ipynb` | NDVI statistical analysis with bell curve visualization |

### Output Directories
- `output_data/` - Generated analysis outputs (CSV, GeoTIFF, visualizations)
- `attached_assets/` - Uploaded boundary files and assets

## Getting Started

### Prerequisites
- Python 3.11+
- Google Earth Engine account and authentication
- JupyterLab environment

### Installation

1. All dependencies are pre-installed via uv package manager

2. Authenticate with Google Earth Engine:
   ```python
   import ee
   ee.Authenticate()
   ee.Initialize(project="your-project-id")
   ```

3. Launch JupyterLab (runs automatically on port 5000)

## Analysis Workflows

### 1. Reclamation Assessment with AlphaEarth Embeddings

Use `Reclamation_Analysis_AEFv4_working.ipynb`:
- Upload field boundary (KML/GeoJSON/SHP)
- Upload lease boundary polygon
- Automatic crop type extraction from AAFC
- Extract 64D AlphaEarth embeddings for lease and background
- Compare using cosine similarity metrics
- Generate recovery trajectory visualization

**Key Features of v4:**
- Uses `selfMask()` to automatically exclude null/masked pixels at edges
- Returns explicit failure states that the analysis loop skips
- Minimum 10 valid pixels required for embedding computation
- Correct A00-A63 band naming format

### 2. Precipitation Context Analysis

Use `Precipitation_Context_Analysis.ipynb`:
- Extract ERA-5 Land precipitation data
- Calculate 10-year baseline statistics (2010-2019)
- Classify conditions (Extremely Dry to Extremely Wet)
- Generate monthly and seasonal anomaly reports

### 3. Background Data Extraction

Use `Background_Data_Extraction.ipynb`:
- Extract AAFC crop history for any location
- Pull ERA-5 precipitation data with anomaly calculations
- Export combined environmental dataset to CSV

### 4. Robust Z-Score Analysis

Use `Reclamation_Assessment_Robust_Z_Score.ipynb`:
- Compare lease performance against background field
- Use Median Absolute Deviation for robust statistics
- Identify anomalous years in reclamation trajectory

## Methodology

### AlphaEarth Embedding Comparison

The platform uses 64-dimensional embeddings from AlphaEarth Foundation to assess reclamation success:

1. **Extract embeddings** for lease area and background (field minus lease)
2. **Compute cosine similarity** between lease and background
3. **Track trajectory** over time (2017-2023)

**Interpretation**:
- Similarity > 0.95: Lease performing equivalently → **Reclamation Success**
- Similarity 0.85-0.95: Lease recovering → **On Track**
- Similarity < 0.85: Lease underperforming → **Needs Attention**

### Precipitation Adjustment

The analysis accounts for weather impacts:
- **Dry years** (< -15% anomaly): Tolerance added for underperformance
- **Normal years** (±15% anomaly): Baseline expectations
- **Wet years** (> +15% anomaly): Higher performance expected

## Output Products

### Generated Files
- `reclamation_analysis_results.csv`: Time series of performance metrics
- `precipitation_context.json`: Weather anomaly data
- GeoTIFF rasters: Spatial analysis outputs

### Visualizations
1. **Recovery Trajectory**: Cosine similarity trends over time
2. **Precipitation Overlay**: Performance metrics with weather context
3. **Anomaly Charts**: Monthly and seasonal precipitation deviations
4. **Summary Tables**: Year-by-year classification and metrics

## Recent Updates

### November 2025
- **v4 notebook** with comprehensive fixes for AlphaEarth extraction
  - Fixed band naming consistently (A00-A63 format)
  - Uses `selfMask()` to automatically exclude null/masked pixels at edges
  - Returns explicit failure states that the analysis loop skips (no zero-vector contamination)
  - Minimum pixel count validation (10+ valid pixels required)
  - Robust lease vs field comparison with proper error handling
- ERA-5 Land precipitation integration for weather context
- Background Data Extraction notebook for environmental data
- Precipitation anomaly classification and adjustment algorithms

## Troubleshooting

### Common Issues

1. **"Band pattern 'embedding_0' did not match any bands"**
   - Solution: Use `Reclamation_Analysis_AEFv4_working.ipynb` which has correct 'A00-A63' format

2. **"No valid crop code found"**
   - Solution: Increase sample_size parameter or check boundary overlap with AAFC data

3. **"Insufficient pixels" warning**
   - This is expected when lease boundary extends beyond valid data coverage
   - The v4 notebook handles this gracefully by skipping invalid years

4. **Precipitation data not loading**
   - Solution: Ensure ERA-5 Land collection access in GEE project

## Dependencies

### Core Libraries
- **Geospatial**: earthengine-api, geemap, geopandas, rasterio, fiona, shapely
- **Data Analysis**: numpy, pandas
- **Visualization**: matplotlib, ipywidgets
- **Notebook Environment**: jupyterlab, notebook

---

*Built with Google Earth Engine, AlphaEarth Foundation, and open-source geospatial tools*
