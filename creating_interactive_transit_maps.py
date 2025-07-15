import geopandas as gpd
import folium
from folium.plugins import MarkerCluster
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Function to create sample transit data with 12 bus stops
def get_sample_data():
    logger.info("Creating sample bus stop data for San Francisco.")
    data = [
        {'id': 1, 'name': 'Market St & 5th St', 'lat': 37.7840, 'lon': -122.4070},
        {'id': 2, 'name': 'Geary Blvd & 33rd Ave', 'lat': 37.7800, 'lon': -122.4920},
        {'id': 3, 'name': 'Mission St & 16th St', 'lat': 37.7650, 'lon': -122.4190},
        {'id': 4, 'name': 'Van Ness Ave & O’Farrell St', 'lat': 37.7850, 'lon': -122.4200},
        {'id': 5, 'name': 'Fulton St & 8th Ave', 'lat': 37.7760, 'lon': -122.4650},
        {'id': 6, 'name': 'Powell St & Geary St', 'lat': 37.7870, 'lon': -122.4080},
        {'id': 7, 'name': '19th Ave & Holloway Ave', 'lat': 37.7210, 'lon': -122.4750},
        {'id': 8, 'name': 'Lombard St & Fillmore St', 'lat': 37.7990, 'lon': -122.4350},
        {'id': 9, 'name': 'Embarcadero & Folsom St', 'lat': 37.7900, 'lon': -122.3910},
        {'id': 10, 'name': 'Balboa St & 25th Ave', 'lat': 37.7765, 'lon': -122.4840},
        {'id': 11, 'name': 'Divisadero St & Sutter St', 'lat': 37.7855, 'lon': -122.4400},
        {'id': 12, 'name': 'Castro St & 24th St', 'lat': 37.7510, 'lon': -122.4350},
    ]
    try:
        gdf = gpd.GeoDataFrame(
            [{'id': d['id'], 'name': d['name'],
              'geometry': gpd.points_from_xy([d['lon']], [d['lat']])[0]} for d in data],
            crs="EPSG:4326"
        )
        logger.info(f"Created GeoDataFrame with {len(gdf)} bus stops.")
        return gdf
    except Exception as e:
        logger.error(f"Failed to create GeoDataFrame: {e}")
        return None

# Main function to create the transit map
def create_transit_map():
    # Get sample data
    gdf = get_sample_data()
    
    # Check if GeoDataFrame is valid
    if gdf is None or gdf.empty:
        logger.error("No valid data to plot. Exiting.")
        return None
    
    # Log GeoDataFrame contents
    logger.info(f"GeoDataFrame head:\n{gdf.head().to_string()}")
    
    # Create a Folium map
    try:
        map_center = [gdf.geometry.y.mean(), gdf.geometry.x.mean()]
        logger.info(f"Map centered at {map_center}")
        transit_map = folium.Map(location=map_center, zoom_start=12, tiles="CartoDB positron")
        
        # Add marker cluster
        marker_cluster = MarkerCluster().add_to(transit_map)
        
        # Add bus stops to the map
        for idx, row in gdf.iterrows():
            try:
                folium.Marker(
                    location=[row.geometry.y, row.geometry.x],
                    popup=row['name'],
                    icon=folium.Icon(color="blue", icon="bus", prefix="fa")
                ).add_to(marker_cluster)
                logger.info(f"Added marker for {row['name']} at ({row.geometry.y}, {row.geometry.x})")
            except Exception as e:
                logger.error(f"Error adding marker for {row['name']}: {e}")
        
        # Save the map
        output_file = Path("transit_map.html")
        transit_map.save(output_file)
        logger.info(f"Map saved as '{output_file}'. File size: {output_file.stat().st_size} bytes.")
        return output_file
    except Exception as e:
        logger.error(f"Failed to create map: {e}")
        return None

# Run the script
if __name__ == "__main__":
    try:
        output = create_transit_map()
        if output:
            logger.info("Script completed successfully. Open 'transit_map.html' in a web browser.")
        else:
            logger.error("Script failed to generate the map.")
    except Exception as e:
        logger.error(f"Script execution failed: {e}")
