# Geospatial Analysis with Google Earth Engine

## Overview
A Python-based Jupyter notebook project for satellite imagery analysis using Google Earth Engine. Includes tools for Sentinel-2 imagery extraction, NDVI analysis, reclamation site assessment using AlphaEarth Foundation embeddings, and robust z-score transformation for comparative field analysis.

## Project Structure
### Analysis Notebooks
- **Background_Data_Extraction.ipynb** - **NEW!** Self-contained notebook for extracting AAFC crop history and ERA-5 precipitation data
- **Precipitation_Context_Analysis.ipynb** - ERA-5 Land precipitation analysis with anomaly detection and classification
- **Reclamation_Assessment_Robust_Z_Score.ipynb** - Robust z-score analysis for lease vs background field comparison using MAD statistics
- **Reclamation_Analysis_AEFv4.ipynb** - **RECOMMENDED** Latest version with comprehensive fixes for AEF extraction (correct band naming, edge handling, null pixel management)
- **Reclamation_Analysis_AEF.ipynb** - Oilfield reclamation assessment using AlphaEarth Foundation 64D embeddings and difference-in-differences methodology
- **Reclamation_Analysis_AEFv2.ipynb** - Simplified analysis with direct lease vs field comparison
- **Reclamation_Analysis_AEFv3.ipynb** - Extended version with additional features
- **Sentinel2_RasterExtractor.ipynb** - Extract Sentinel-2 imagery from Google Earth Engine (NDVI, NDMI, RGB products)
- **Multi_Year_ProductivityRaster.ipynb** - Analyze multi-year NDVI productivity data
- **NDVI_Mean_and_St_Dev_Bell_Curve_V1.ipynb** - Statistical analysis of NDVI data with bell curve visualization

### Python Modules
- **precipitation_analysis.py** - ERA-5 precipitation data extraction and anomaly calculation
- **integrate_precipitation.py** - Integration utilities for weather-adjusted analysis

## Technology Stack
- **Python 3.11** with JupyterLab
- **Geospatial Libraries**: geopandas, rasterio, fiona, shapely
- **Google Earth Engine**: earthengine-api, geemap
- **Data Analysis**: numpy, pandas, matplotlib
- **Widgets**: ipywidgets for interactive file uploads and controls

## Dependencies
All required dependencies are installed via uv package manager:
- jupyterlab
- geopandas, rasterio, fiona, shapely
- earthengine-api, geemap
- ipywidgets, matplotlib, numpy, pandas

## Running the Project
The project runs on JupyterLab server on port 5000. Simply start the workflow to launch JupyterLab and access the notebooks.

## Key Features
1. **Sentinel-2 Data Extraction**: Query and download NDVI, NDMI, and RGB imagery from Google Earth Engine
2. **Multi-Year Analysis**: Analyze productivity trends over multiple years
3. **Statistical Analysis**: Bell curve analysis with robust z-scores using Median Absolute Deviation
4. **Interactive Widgets**: Upload KML, GeoJSON, or SHP files for area of interest (AOI) definition

## Notes
- Google Earth Engine authentication is required for the Sentinel2_RasterExtractor notebook
- Notebooks are originally designed for Google Colab but adapted for local JupyterLab use
- Output files (GeoTIFF, rasters) are saved locally and can be downloaded

## Reclamation Analysis Features
The Reclamation_Analysis_AEF.ipynb notebook provides:
- **File Upload Widgets**: Upload field and lease boundary polygons (KML, GeoJSON, SHP/ZIP)
- **Crop History Extraction**: Automatically identify crop types from AAFC Annual Crop Inventory (2017-2023)
- **Regional Reference Building**: Sample healthy cropland of same type within configurable radius
- **Difference-in-Differences Analysis**: Compare lease performance vs background field vs regional reference
- **Recovery Trajectory Visualization**: Track reclamation progress over time with cosine similarity metrics
- **Smart Fallback**: Automatically expands search radius if insufficient regional samples found

## Precipitation Context Features (NEW)
The Precipitation_Context_Analysis.ipynb notebook provides:
- **ERA-5 Land Integration**: Monthly precipitation data extraction at 11km resolution
- **Baseline Statistics**: 10-year normal period calculation (2010-2019)
- **Anomaly Detection**: Classification of dry/wet conditions relative to normal
- **Growing Season Focus**: April-October precipitation analysis for crop assessment
- **Multi-Year Comparison**: Track precipitation patterns across analysis years
- **Performance Adjustment**: Normalize reclamation metrics for weather effects
- **Integrated Visualization**: Combined precipitation and performance visualizations

## Methodology
Uses Google's AlphaEarth Foundation 64D embeddings to assess whether reclaimed oilfield leases are performing equivalently to surrounding healthy cropland, accounting for regional crop-specific conditions.

## Recent Changes
- 2025-11-25: Created Reclamation_Analysis_AEFv4.ipynb with comprehensive fixes
  - Fixed AlphaEarth band naming to use 'A00-A63' format consistently throughout
  - Uses `selfMask()` to automatically exclude null/masked edge pixels
  - Returns `embedding=None` on failure so analysis loop skips invalid years (no zero-vector contamination)
  - Added minimum pixel count validation (10+ valid pixels required)
  - Rebuilt lease vs field comparison with proper error handling and status reporting
  - Clear status messages for each extraction step
- 2025-11-17: Added ERA-5 Land precipitation context analysis and background data extraction
  - Created Background_Data_Extraction.ipynb - self-contained notebook for extracting AAFC crop and ERA-5 precipitation data
  - Fixed Earth Engine boolean evaluation issues for proper data extraction
  - Added configurable date ranges for both AAFC and precipitation analysis
  - Implemented CSV export for combined environmental dataset
  - Created precipitation_analysis.py module for ERA-5 data extraction
  - Added Precipitation_Context_Analysis.ipynb for weather anomaly detection
  - Implemented precipitation anomaly classification (Extremely Dry to Extremely Wet)
  - Created integrate_precipitation.py for combining weather with reclamation analysis
  - Updated README with comprehensive documentation
- 2025-11-05: Fixed AlphaEarth band naming issue and added simplified analysis option
  - Updated band references from 'embedding_0' format to 'A00' format to match AlphaEarth dataset
  - Fixed in both Reclamation_Analysis_AEF.ipynb and Reclamation_Analysis_AEFv2.ipynb
  - Added simplified analysis option in v2 notebook: direct lease vs field comparison without regional reference
  - Simplified approach makes analysis clearer and easier to interpret
  - This resolves the "Band pattern 'embedding_0' did not match any bands" error
- 2025-11-03: Added Reclamation_Analysis_AEF.ipynb for oilfield reclamation assessment
  - Integrated AlphaEarth Foundation 64D embeddings
  - Connected AAFC Annual Crop Inventory for crop type identification
  - Implemented difference-in-differences methodology
  - Built interactive file upload workflow with validation
  - Created comprehensive visualization dashboard
- 2025-10-18: Initial setup for Replit environment completed
  - Python 3.11 with all required packages installed via uv
  - Jupyter Notebook server configured on port 5000
  - All geospatial dependencies installed (geopandas, rasterio, fiona, shapely)
  - Google Earth Engine libraries installed (earthengine-api, geemap)
  - Deployment configured for VM target to keep notebook server running
