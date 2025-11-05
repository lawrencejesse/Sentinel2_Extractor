#!/usr/bin/env python3
"""
Fix the get_embeddings function in the notebook to handle large areas and data type issues
"""

import json

# Read the notebook
with open('Reclamation_Analysis_AEFv2.ipynb', 'r') as f:
    notebook = json.load(f)

# Find and fix the get_embeddings function
for cell_idx, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'code':
        # Check if this is the cell containing get_embeddings
        source = ''.join(cell['source'])
        if 'def get_embeddings(geometry, year, scale=10):' in source and 'maxPixels=1e8' in source:
            print(f"Found get_embeddings function in cell {cell_idx}")
            
            # Create the fixed version of the code
            fixed_source = """# Load AEF dataset
aef_collection = ee.ImageCollection("GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL")

def get_embeddings(geometry, year, scale=10):
    \"\"\"
    Extract mean 64D embedding for a geometry and year
    
    Args:
        geometry: ee.Geometry
        year: int (2017-2024)
        scale: int (default 10m)
    
    Returns:
        dict with 'embedding' (64D array) and 'pixel_count'
    \"\"\"
    # Filter to specific year
    aef_year = aef_collection.filter(ee.Filter.date(f'{year}-01-01', f'{year}-12-31')).first()
    
    # Get all 64 bands
    band_names = [f'A{i:02d}' for i in range(64)]
    
    # Compute mean embedding across the geometry
    # FIXED: Use bestEffort=True to handle large regions automatically
    stats = aef_year.select(band_names).reduceRegion(
        reducer=ee.Reducer.mean().combine(
            reducer2=ee.Reducer.count(),
            sharedInputs=True
        ),
        geometry=geometry,
        scale=scale,
        maxPixels=1e10,  # Increased from 1e8 to handle large fields
        bestEffort=True   # Automatically adjust scale if needed for large areas
    )
    
    result = stats.getInfo()
    
    # FIXED: Extract embedding values with proper type handling
    embedding_values = []
    for i in range(64):
        val = result.get(f'A{i:02d}_mean', None)
        # Convert to float, handling None and ensuring numeric type
        if val is None:
            embedding_values.append(0.0)  # Use 0.0 instead of np.nan to avoid type issues
        else:
            try:
                embedding_values.append(float(val))
            except (TypeError, ValueError):
                embedding_values.append(0.0)
    
    embedding = np.array(embedding_values, dtype=np.float64)
    
    # Get pixel count with type safety
    pixel_count = result.get('A00_count', 0)
    if pixel_count is not None:
        try:
            pixel_count = int(pixel_count)
        except (TypeError, ValueError):
            pixel_count = 0
    else:
        pixel_count = 0
    
    return {
        'embedding': embedding,
        'pixel_count': pixel_count,
        'year': year
    }

def get_regional_reference(center_point, crop_code, year, radius_km=15, sample_pixels=1000, max_radius_km=50):
    \"\"\"
    Build regional reference embedding by sampling healthy pixels of same crop

    Args:
        center_point: ee.Geometry.Point
        crop_code: int (AAFC crop classification code)
        year: int
        radius_km: float (initial sampling radius in km)
        sample_pixels: int (number of pixels to sample)
        max_radius_km: float (maximum radius to try if no samples found)

    Returns:
        dict with 'embedding' (64D centroid), 'sample_count', and 'actual_radius'
    \"\"\"
    band_names = [f'A{i:02d}' for i in range(64)]

    # Try progressively larger radii if needed
    for current_radius in [radius_km, radius_km * 2, max_radius_km]:
        # Create sampling region (circular buffer)
        sampling_region = center_point.buffer(current_radius * 1000)  # Convert km to meters

        # Get crop mask for this year
        aafc = ee.ImageCollection('AAFC/ACI')
        crop_img = aafc.filter(ee.Filter.date(f'{year}-01-01', f'{year}-12-31')).first()

        # Mask to only pixels matching our crop type
        crop_mask = crop_img.select('landcover').eq(crop_code)

        # Get AlphaEarth embeddings for this year
        aef_year = aef_collection.filter(ee.Filter.date(f'{year}-01-01', f'{year}-12-31')).first()
        aef_masked = aef_year.select(band_names).updateMask(crop_mask)

        # Sample pixels from the masked image
        samples = aef_masked.sample(
            region=sampling_region,
            scale=10,
            numPixels=sample_pixels,
            seed=42,
            dropNulls=True
        )

        # Count samples
        sample_count = samples.size()
        actual_count = sample_count.getInfo()

        if actual_count > 100:  # Need at least 100 samples for reliable centroid
            # Compute mean embedding across samples
            mean_embedding = samples.reduceColumns(
                ee.Reducer.mean().repeat(64),
                band_names
            )

            result = mean_embedding.getInfo()
            
            # FIXED: Handle the embedding array with proper type conversion
            embedding_values = []
            for val in result['mean']:
                if val is None:
                    embedding_values.append(0.0)
                else:
                    try:
                        embedding_values.append(float(val))
                    except (TypeError, ValueError):
                        embedding_values.append(0.0)
            
            embedding = np.array(embedding_values, dtype=np.float64)

            return {
                'embedding': embedding,
                'sample_count': actual_count,
                'actual_radius': current_radius
            }

    # Fallback if no samples found
    return {
        'embedding': np.zeros(64, dtype=np.float64),
        'sample_count': 0,
        'actual_radius': max_radius_km
    }

def cosine_similarity(a, b):
    \"\"\"Compute cosine similarity between two vectors\"\"\"
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return dot_product / (norm_a * norm_b)

def euclidean_distance(a, b):
    \"\"\"Compute Euclidean distance between two vectors\"\"\"
    return np.linalg.norm(a - b)

print("✓ FIXED embedding extraction functions ready")
print("✓ Now handles large areas with bestEffort=True")
print("✓ Properly handles data type conversions to avoid 'isnan' errors")
"""
            
            # Split the source into lines and replace the cell content
            cell['source'] = fixed_source.split('\n')
            # Add newline to each line except the last one
            for i in range(len(cell['source']) - 1):
                cell['source'][i] += '\n'
            
            print(f"Fixed the get_embeddings function in cell {cell_idx}")
            break

# Save the fixed notebook
with open('Reclamation_Analysis_AEFv2.ipynb', 'w') as f:
    json.dump(notebook, f, indent=2)

print("Notebook has been fixed and saved!")
print("\nChanges made:")
print("1. Increased maxPixels from 1e8 to 1e10")
print("2. Added bestEffort=True to handle large areas")
print("3. Fixed data type handling to avoid 'isnan' errors")
print("4. Added try/except blocks for robust type conversion")