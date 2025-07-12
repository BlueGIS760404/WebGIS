import geopandas as gpd
import ee
from shapely.geometry import mapping
import folium

# Initialize Google Earth Engine
ee.Initialize()

# Load the vector data (shapefile with administrative boundaries)
vector_path = 'E:\Freelancing\P_05_6.18.2025\data\shp/county_new.shp'  # Replace with your shapefile path
zones = gpd.read_file(vector_path)

# Ensure geometries are valid (correct invalid geometries if needed)
zones['geometry'] = zones['geometry'].apply(lambda geom: geom if geom.is_valid else geom.buffer(0))

# Ensure the CRS is WGS84 (EPSG:4326) for GEE compatibility
zones = zones.to_crs(epsg=4326)

# Load DEM dataset from Google Earth Engine (SRTM DEM in this case)
dem = ee.Image("USGS/SRTMGL1_003")  # You can also use "NASA/ASTER_GDEM"

# Function to extract DEM data from Earth Engine
def get_dem_array(dem_image, region):
    """Extract DEM data from GEE and convert to numpy array."""
    dem_array = dem_image.reduceRegion(
        reducer=ee.Reducer.mean(),  # You can replace with other reducers like sum, etc.
        geometry=region,
        scale=30,  # Resolution of the DEM (SRTM is 30m)
        maxPixels=1e8
    ).getInfo()
    
    return dem_array

# Initialize a list to store results
elevation_results = []

# Loop through each administrative zone (polygon)
for idx, zone in zones.iterrows():
    # Convert the current zone's geometry to GeoJSON format for Earth Engine
    aoi_geojson = mapping(zone['geometry'])

    # Clip the DEM to the current administrative boundary
    dem_clipped = dem.clip(ee.Geometry(aoi_geojson))

    # Get the DEM statistics (mean elevation) for the current zone
    dem_stats = get_dem_array(dem_clipped, aoi_geojson)

    # Extract the mean elevation and append it to the results list
    mean_elevation = dem_stats.get('elevation', None)
    if mean_elevation is not None:
        # Replace 'zone_id' with the correct column name from your shapefile
        elevation_results.append({
            'zone_id': zone['County_Nam'],  # Replace 'NAME' with the correct column name
            'mean_elevation': mean_elevation,
            'geometry': zone['geometry']  # Keep geometry for mapping
        })

# Create a base map using folium (centered around the first zone)
m = folium.Map(location=[zones.geometry.centroid.y.mean(), zones.geometry.centroid.x.mean()],
               zoom_start=10)

# Loop through the results to add each zone with its mean elevation to the map
for result in elevation_results:
    # Get the geometry (polygon) and mean elevation
    geo = result['geometry']
    mean_elevation = result['mean_elevation']
    
    # Create a popup with larger font size
    popup_content = f"""
    <div style="font-size: 18px; font-weight: bold; color: #333;">
        <strong>Zone: {result['zone_id']}</strong><br>
        <strong>Mean Elevation: {mean_elevation:.2f} meters</strong>
    </div>
    """
    
    # Add the polygon to the map with the custom popup
    folium.GeoJson(
        geo,
        tooltip=popup_content,  # Show the elevation on hover
        style_function=lambda x: {
            'fillColor': 'green' if mean_elevation > 1500 else 'red',  # Style based on elevation
            'color': 'black',  # Border color
            'weight': 2,
            'fillOpacity': 0.4
        }
    ).add_to(m)

# Save the map as an HTML file
m.save('mean_elevation_map.html')

# Display the map (in Jupyter, you can directly display `m` without saving)
m
