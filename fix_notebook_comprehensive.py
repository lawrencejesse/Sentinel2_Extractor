#!/usr/bin/env python3
"""
Fix Multi_Year_ProductivityRaster.ipynb to work in both Jupyter and Colab environments
"""
import json
import sys

def fix_notebook():
    with open('Multi_Year_ProductivityRaster.ipynb', 'r') as f:
        notebook = json.load(f)
    
    fixes_applied = []
    
    # Fix 1: Update imports to include all necessary libraries
    imports_cell_code = """# Imports for both Jupyter and Colab environments
%pip install -q geopandas rasterio fiona shapely numpy

import geopandas
import rasterio
import rasterio.warp
import rasterio.mask
import fiona
from shapely.geometry import shape
import numpy as np
import os
import ipywidgets as widgets
from IPython.display import display
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Detect environment (Colab vs Jupyter)
try:
    from google.colab import files
    IN_COLAB = True
    print("Running in Google Colab environment")
except ImportError:
    IN_COLAB = False
    print("Running in Jupyter environment")"""
    
    # Fix 2: Add skip_alignment widget creation cell (add before file upload widgets)
    widget_setup_code = """# Create configuration widgets
skip_alignment_widget = widgets.Checkbox(
    value=False,
    description='Skip Alignment',
    tooltip='Skip the reprojection and alignment step if rasters are already aligned'
)

display(skip_alignment_widget)
print("Configuration widgets created.")"""
    
    # Fix 3: Update FileUpload widget creation to be compatible with both environments
    file_upload_widgets_code = """# Create file upload widgets
aoi_upload = widgets.FileUpload(
    accept='.kml,.geojson,.shp',
    multiple=False,
    description='Upload AOI Polygon (KML, GeoJSON, or SHP)'
)

ndvi_uploads = widgets.FileUpload(
    accept='.tif,.tiff',
    multiple=True,
    description='Upload NDVI Rasters (GeoTIFFs)'
)

display(aoi_upload)
display(ndvi_uploads)
print("File upload widgets created. Please upload your AOI polygon and NDVI rasters.")"""
    
    # Fix 4: Update loading cell to work with both environments
    loading_cell_code = """aoi_gdf = None
original_ndvi_datasets = []
memfiles = []  # Keep MemoryFile objects alive

# Function to handle different widget structures (Jupyter vs Colab)
def get_file_content(upload_widget, is_multiple=False):
    \"\"\"Extract file content from upload widget, handling both Jupyter and Colab formats\"\"\"
    files_data = []
    
    if upload_widget.value:
        # Check if it's Colab format (dict) or Jupyter format (tuple)
        if isinstance(upload_widget.value, dict):
            # Colab format: {'filename': {'content': bytes}}
            for filename, file_info in upload_widget.value.items():
                files_data.append({
                    'name': filename,
                    'content': file_info['content']
                })
        else:
            # Jupyter format: ({'name': str, 'content': bytes}, ...)
            for file_dict in upload_widget.value:
                files_data.append({
                    'name': file_dict['name'],
                    'content': file_dict['content']
                })
    
    return files_data[0] if files_data and not is_multiple else files_data

# Load AOI polygon
aoi_file = get_file_content(aoi_upload, is_multiple=False)
if aoi_file:
    try:
        with fiona.io.MemoryFile(aoi_file['content']) as memfile:
            aoi_gdf = geopandas.read_file(memfile)
        print(f"AOI polygon '{aoi_file['name']}' loaded successfully.")
        print(f"AOI CRS: {aoi_gdf.crs}")
    except Exception as e:
        print(f"Error loading AOI file: {e}")
else:
    print("No AOI file uploaded. Skipping AOI loading.")

# Load NDVI rasters
ndvi_files = get_file_content(ndvi_uploads, is_multiple=True)
if ndvi_files:
    for file_data in ndvi_files:
        try:
            # Keep MemoryFile alive by storing it
            memfile = rasterio.io.MemoryFile(file_data['content'])
            dataset = memfile.open()
            original_ndvi_datasets.append(dataset)
            memfiles.append(memfile)  # Important: Keep memfile alive!
            print(f"NDVI raster '{file_data['name']}' loaded successfully.")
        except Exception as e:
            print(f"Error loading NDVI file '{file_data['name']}': {e}")
else:
    print("No NDVI files uploaded. Skipping NDVI loading.")

# Initialize ndvi_datasets for later use
ndvi_datasets = []

# Summary
if aoi_gdf is not None and original_ndvi_datasets:
    print(f"\\nSummary: Loaded {len(original_ndvi_datasets)} NDVI raster(s) and 1 AOI polygon.")
elif original_ndvi_datasets:
    print(f"\\nSummary: Loaded {len(original_ndvi_datasets)} NDVI raster(s), no AOI polygon.")
elif aoi_gdf is not None:
    print(f"\\nSummary: Loaded 1 AOI polygon, no NDVI rasters.")
else:
    print(f"\\nSummary: No files loaded.")"""
    
    # Fix 5: Update alignment cell to ensure proper data handling
    alignment_cell_code = """import rasterio.warp

aligned_ndvi_arrays = []
target_crs = None
target_transform = None
target_width = None
target_height = None

if not original_ndvi_datasets:
    print("No NDVI datasets loaded. Skipping reprojection and alignment.")
    ndvi_datasets = original_ndvi_datasets
else:
    if skip_alignment_widget.value:
        print("Skipping reprojection and alignment as requested.")
        # If alignment is skipped, use the original datasets for subsequent steps
        ndvi_datasets = original_ndvi_datasets
        # Get target CRS and transform from the first original dataset
        if ndvi_datasets:
            target_crs = ndvi_datasets[0].crs
            target_transform = ndvi_datasets[0].transform
            target_width = ndvi_datasets[0].width
            target_height = ndvi_datasets[0].height
            print(f"Using CRS and transform from first dataset: {target_crs}")
    else:
        print("Performing reprojection and alignment...")
        # Get CRS and transform from the first dataset
        first_dataset = original_ndvi_datasets[0]
        target_crs = first_dataset.crs
        target_transform = first_dataset.transform
        target_width = first_dataset.width
        target_height = first_dataset.height
        
        print(f"Target CRS: {target_crs}")
        print(f"Target dimensions: {target_width} x {target_height}")
        
        # Read all datasets and align them
        for i, dataset in enumerate(original_ndvi_datasets):
            try:
                if i == 0:
                    # First dataset sets the reference
                    aligned_ndvi_arrays.append(dataset.read(1))
                    print(f"Dataset 0 (reference) read successfully.")
                else:
                    # Reproject other datasets to match the first
                    reprojected_data = np.empty((target_height, target_width), dtype=dataset.dtypes[0])
                    
                    rasterio.warp.reproject(
                        source=rasterio.band(dataset, 1),
                        destination=reprojected_data,
                        src_transform=dataset.transform,
                        src_crs=dataset.crs,
                        dst_transform=target_transform,
                        dst_crs=target_crs,
                        resampling=rasterio.warp.Resampling.bilinear
                    )
                    aligned_ndvi_arrays.append(reprojected_data)
                    print(f"Dataset {i} reprojected and aligned.")
            except Exception as e:
                print(f"Error processing dataset {i}: {e}")
        
        # Use aligned arrays for subsequent steps
        ndvi_datasets = aligned_ndvi_arrays
        print(f"\\nAlignment complete: {len(ndvi_datasets)} datasets ready for processing.")"""
    
    # Fix 6: Update clipping cell to handle both dataset types properly
    clipping_cell_code = """import rasterio.mask

clipped_ndvi_data_and_transforms = []

if aoi_gdf is None or not ndvi_datasets:
    print("AOI polygon or NDVI datasets not available. Skipping clipping process.")
else:
    if target_crs is None or target_transform is None:
        print("Target CRS or Transform not defined. Cannot clip.")
    else:
        # Ensure the AOI is in the same CRS as the rasters
        if aoi_gdf.crs != target_crs:
            try:
                aoi_gdf = aoi_gdf.to_crs(target_crs)
                print(f"AOI polygon reprojected to target CRS: {target_crs}")
            except Exception as e:
                print(f"Error reprojecting AOI polygon: {e}")
                aoi_gdf = None
        
        if aoi_gdf is not None:
            # Get the geometry for masking
            geometries = aoi_gdf.geometry.values
            
            for i, dataset_or_array in enumerate(ndvi_datasets):
                try:
                    if hasattr(dataset_or_array, 'read'):
                        # It's a rasterio DatasetReader (when alignment was skipped)
                        clipped_data, clipped_transform = rasterio.mask.mask(
                            dataset_or_array, geometries, crop=True, nodata=np.nan
                        )
                        clipped_data = clipped_data[0]  # Get first band
                        clipped_ndvi_data_and_transforms.append((clipped_data, clipped_transform))
                        print(f"NDVI dataset {i} clipped successfully.")
                    else:
                        # It's a numpy array (when alignment was performed)
                        # Create a temporary in-memory dataset for clipping
                        height, width = dataset_or_array.shape
                        dtype = dataset_or_array.dtype
                        
                        with rasterio.MemoryFile() as memfile:
                            with memfile.open(
                                driver='GTiff',
                                height=height,
                                width=width,
                                count=1,
                                dtype=dtype,
                                crs=target_crs,
                                transform=target_transform
                            ) as tmp_dataset:
                                tmp_dataset.write(dataset_or_array, 1)
                                
                                # Perform clipping
                                clipped_data, clipped_transform = rasterio.mask.mask(
                                    tmp_dataset, geometries, crop=True, nodata=np.nan
                                )
                                clipped_data = clipped_data[0]  # Get first band
                        
                        clipped_ndvi_data_and_transforms.append((clipped_data, clipped_transform))
                        print(f"NDVI array {i} clipped successfully.")
                        
                except Exception as e:
                    print(f"Error clipping item {i}: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Replace ndvi_datasets with clipped data
            ndvi_datasets = clipped_ndvi_data_and_transforms
            print(f"\\nClipping complete: {len(ndvi_datasets)} datasets clipped to AOI.")"""
    
    # Now apply fixes to the notebook
    cell_index = 0
    
    # First, find and update the imports cell
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source'])
            if 'import geopandas' in source and 'import rasterio' in source and i < 10:
                cell['source'] = imports_cell_code.split('\n')
                cell['source'] = [line + '\n' for line in cell['source']]
                fixes_applied.append("Updated imports cell for environment compatibility")
                break
    
    # Insert widget setup cell before file upload widgets
    widget_setup_inserted = False
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source'])
            if 'aoi_upload = widgets.FileUpload' in source and not widget_setup_inserted:
                # Insert the widget setup cell before this one
                new_cell = {
                    'cell_type': 'code',
                    'metadata': {},
                    'source': [line + '\n' for line in widget_setup_code.split('\n')],
                    'execution_count': None,
                    'outputs': []
                }
                notebook['cells'].insert(i, new_cell)
                widget_setup_inserted = True
                fixes_applied.append("Added skip_alignment widget setup")
                break
    
    # Update file upload widgets cell
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source'])
            if 'aoi_upload = widgets.FileUpload' in source:
                cell['source'] = file_upload_widgets_code.split('\n')
                cell['source'] = [line + '\n' for line in cell['source']]
                fixes_applied.append("Updated file upload widgets")
                break
    
    # Update loading cell
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source'])
            if 'aoi_gdf = None' in source and 'original_ndvi_datasets' in source:
                cell['source'] = loading_cell_code.split('\n')
                cell['source'] = [line + '\n' for line in cell['source']]
                fixes_applied.append("Fixed loading cell for both environments")
                break
    
    # Update alignment cell
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source'])
            if 'aligned_ndvi_arrays = []' in source and 'target_crs = None' in source:
                cell['source'] = alignment_cell_code.split('\n')
                cell['source'] = [line + '\n' for line in cell['source']]
                fixes_applied.append("Updated alignment cell")
                break
    
    # Update clipping cell
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source'])
            if 'clipped_ndvi_data_and_transforms = []' in source and 'rasterio.mask' in source:
                cell['source'] = clipping_cell_code.split('\n')
                cell['source'] = [line + '\n' for line in cell['source']]
                fixes_applied.append("Updated clipping cell")
                break
    
    # Save the fixed notebook
    with open('Multi_Year_ProductivityRaster.ipynb', 'w') as f:
        json.dump(notebook, f, indent=2)
    
    print("✅ Notebook fixed successfully!")
    print("\nFixes applied:")
    for fix in fixes_applied:
        print(f"  - {fix}")
    
    return True

if __name__ == "__main__":
    success = fix_notebook()
    sys.exit(0 if success else 1)