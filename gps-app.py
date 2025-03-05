import time
import streamlit as st
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from geopy.geocoders import Nominatim
import folium
from folium.plugins import MarkerCluster

def geocode_with_retry(geolocator, location, retries=3, delay=2):
    """Try geocoding a location with retry logic."""
    for _ in range(retries):
        try:
            return geolocator.geocode(location)
        except GeocoderTimedOut:
            st.warning(f"Geocoding timed out for {location}, retrying...")
            time.sleep(delay)  # Wait for `delay` seconds before retrying
        except GeocoderUnavailable:
            st.warning(f"Geocoder service unavailable for {location}, retrying...")
            time.sleep(delay)
    st.error(f"Geocoding failed for {location} after {retries} retries")
    return None

def create_map(source, destination):
    """Create map with source and destination."""
    geolocator = Nominatim(user_agent="my_gps_app", timeout=10)  # Increased timeout to 10 seconds

    # Get location for source and destination with retry logic
    source_location = geocode_with_retry(geolocator, source)
    destination_location = geocode_with_retry(geolocator, destination)

    if not source_location or not destination_location:
        raise Exception("Unable to geocode source or destination")

    # Create a map centered between source and destination
    m = folium.Map(location=[(source_location.latitude + destination_location.latitude) / 2,
                             (source_location.longitude + destination_location.longitude) / 2],
                   zoom_start=13)

    # Add markers for source and destination
    folium.Marker([source_location.latitude, source_location.longitude],
                  popup=f"Source: {source}",
                  icon=folium.Icon(color='blue')).add_to(m)
    folium.Marker([destination_location.latitude, destination_location.longitude],
                  popup=f"Destination: {destination}",
                  icon=folium.Icon(color='red')).add_to(m)

    return m

# Streamlit UI
st.title("GPS Location Mapper")

source = st.text_input("Enter Source Location", "Kolkata")
destination = st.text_input("Enter Destination Location", "Delhi")

if st.button("Create Map"):
    try:
        # Create the map based on user input
        map_object = create_map(source, destination)

        # Display map in Streamlit
        folium_map = map_object._repr_html_()  # Get HTML representation of the map
        st.components.v1.html(folium_map, width=700, height=500)
    except Exception as e:
        st.error(f"Error: {e}")
