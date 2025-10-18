# Sentinel2_Extractor

## Overview
A Python-based Jupyter notebook project for extracting and analyzing Sentinel-2 satellite imagery data using Google Earth Engine. This project provides tools for geospatial analysis, NDVI calculations, and multi-year productivity raster analysis.

## Project Structure
- **Sentinel2_RasterExtractor.ipynb** - Main tool for extracting Sentinel-2 imagery from Google Earth Engine (NDVI, NDMI, RGB products)
- **Multi_Year_ProductivityRaster.ipynb** - Analyzes multi-year NDVI productivity data
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

## Recent Changes
- 2025-10-18: Initial setup for Replit environment completed
  - Python 3.11 with all required packages installed via uv
  - Jupyter Notebook server configured on port 5000
  - All geospatial dependencies installed (geopandas, rasterio, fiona, shapely)
  - Google Earth Engine libraries installed (earthengine-api, geemap)
  - Deployment configured for VM target to keep notebook server running
