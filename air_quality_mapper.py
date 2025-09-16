import requests 
import folium

# Xweather API credentials
CLIENT_ID = 'GyYCCFuX6uoVBxFYMTsNZ'
CLIENT_SECRET = 'gSdEkMSJOy2tcRoO0PsRBg7Z3GOcR16Xqr1Bh3r6'

# Indian cities + neighboring high AQI cities
cities = {
    # Top 10 Indian cities
    "Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
    "Bengaluru": (12.9716, 77.5946),
    "Kolkata": (22.5726, 88.3639),
    "Chennai": (13.0827, 80.2707),
    "Hyderabad": (17.3850, 78.4867),
    "Pune": (18.5204, 73.8567),
    "Ahmedabad": (23.0225, 72.5714),
    "Jaipur": (26.9124, 75.7873),
    "Lucknow": (26.8467, 80.9462),
    # Additional 5 Indian cities (extremes)
    "Varanasi": (25.3176, 82.9739),
    "Kanpur": (26.4499, 80.3319),
    "Gurugram": (28.4595, 77.0266),
    "Shimla": (31.1048, 77.1734),
    "Gangtok": (27.3389, 88.6065),
    # Neighboring cities with AQI often >100
    "Karachi, Pakistan": (24.8607, 67.0011),
    "Dhaka, Bangladesh": (23.8103, 90.4125),
    "Kathmandu, Nepal": (27.7172, 85.3240),
    "Colombo, Sri Lanka": (6.9271, 79.8612),
    "Thimphu, Bhutan": (27.4728, 89.6390),
}

# AQI thresholds for each pollutant (simplified)
def classify_aqi(value):
    if value <= 50:
        return 'Good'
    elif value <= 100:
        return 'Moderate'
    elif value <= 150:
        return 'Unhealthy for Sensitive Groups'
    elif value <= 200:
        return 'Unhealthy'
    elif value <= 300:
        return 'Very Unhealthy'
    else:
        return 'Hazardous'

# Function to fetch AQI data from Xweather API
def fetch_aqi(lat, lon):
    url = "https://api.aerisapi.com/airquality/"
    params = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'p': f"{lat},{lon}",
        'limit': 1
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if data['success']:
            period = data['response'][0]['periods'][0]
            aqi = period['aqi']
            
            if 'category' in period:
                category = period['category']
            elif 'categories' in period and 'value' in period['categories']:
                category = period['categories']['value']
            else:
                category = classify_aqi(aqi)
                
            return aqi, category
        else:
            print(f"API Error: {data['error']['description']}")
            return None, None
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None, None
    except (KeyError, IndexError) as e:
        print(f"Error parsing response: {e}")
        print("Response keys:", list(data.keys()) if 'data' in locals() else "No data")
        if 'data' in locals() and 'response' in data:
            print("Response structure:", data['response'])
        return None, None

# Create Folium map
m = folium.Map(location=[23, 82], zoom_start=5)

for city, (lat, lon) in cities.items():
    aqi, category = fetch_aqi(lat, lon)
    if aqi is not None:
        # Only show AQI number, category separately
        tooltip_text = f"""
        <div style="font-size:16px; font-weight:bold;">
            {city}<br>
            AQI: {aqi}<br>
            Category: {category}
        </div>
        """

        if aqi <= 50:
            color = "green"
        elif aqi <= 100:
            color = "yellow"
        elif aqi <= 150:
            color = "orange"
        elif aqi <= 200:
            color = "red"
        elif aqi <= 300:
            color = "purple"
        else:
            color = "darkred"

        folium.CircleMarker(
            location=[lat, lon],
            radius=8,
            color="black",
            weight=1,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            tooltip=tooltip_text
        ).add_to(m)
        print(f"✅ Added {city} with AQI: {aqi}")
    else:
        print(f"No AQI data for {city}")

# Save map
m.save("real_time_aqi_map.html")
print("✅ Map saved as 'real_time_aqi_map.html'. Open in your browser.")
