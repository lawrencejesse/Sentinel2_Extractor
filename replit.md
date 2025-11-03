# Geospatial Analysis with Google Earth Engine

## Overview
A Python-based Jupyter notebook project for satellite imagery analysis using Google Earth Engine. Includes tools for Sentinel-2 imagery extraction, NDVI analysis, and cutting-edge reclamation site assessment using AlphaEarth Foundation embeddings.

## Project Structure
- **Reclamation_Analysis_AEF.ipynb** - **NEW!** Oilfield reclamation assessment using AlphaEarth Foundation 64D embeddings and difference-in-differences methodology
- **Sentinel2_RasterExtractor.ipynb** - Extract Sentinel-2 imagery from Google Earth Engine (NDVI, NDMI, RGB products)
- **Multi_Year_ProductivityRaster.ipynb** - Analyze multi-year NDVI productivity data
- **NDVI_Mean_and_St_Dev_Bell_Curve_V1.ipynb** - Statistical analysis of NDVI data with bell curve visualization

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

## Reclamation Analysis Features (NEW)
The Reclamation_Analysis_AEF.ipynb notebook provides:
- **File Upload Widgets**: Upload field and lease boundary polygons (KML, GeoJSON, SHP/ZIP)
- **Crop History Extraction**: Automatically identify crop types from AAFC Annual Crop Inventory (2017-2023)
- **Regional Reference Building**: Sample healthy cropland of same type within configurable radius
- **Difference-in-Differences Analysis**: Compare lease performance vs background field vs regional reference
- **Recovery Trajectory Visualization**: Track reclamation progress over time with cosine similarity metrics
- **Smart Fallback**: Automatically expands search radius if insufficient regional samples found

## Methodology
Uses Google's AlphaEarth Foundation 64D embeddings to assess whether reclaimed oilfield leases are performing equivalently to surrounding healthy cropland, accounting for regional crop-specific conditions.

## Recent Changes
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
