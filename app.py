import streamlit as st
import folium
import pandas as pd
from folium.plugins import HeatMap, MarkerCluster
from streamlit_folium import st_folium
import time

@st.cache_data  # Cache the data loading
def load_data():
    start_time = time.time()
    
    df = pd.read_csv("cleaned_df.csv", engine="pyarrow")
    # df['YEAR'] = pd.to_numeric(df['YEAR'], errors='coerce')
    finish_time = round(time.time() - start_time, 2)
    st.write(f"finished reading dataset, {finish_time} seconds")
    return df

@st.cache_data  # Cache the filtered data
def filter_data(data, year):
    return data[data['YEAR'].astype(int) == int(year)]

@st.cache_data
def create_crime_map(df_year):
    """Create a folium map with crime data for selected year"""
    
    if len(df_year) > 0:
        # Create base map centered on mean coordinates
        m = folium.Map(
            location=[df_year['Lat'].mean(), df_year['Long'].mean()],
            zoom_start=12,
            prefer_canvas=True
        )
        
        # Add crime markers with clustering
        marker_cluster = MarkerCluster().add_to(m)
        for idx, row in df_year.iterrows():
            folium.Marker(
                [row['Lat'], row['Long']]
            ).add_to(marker_cluster)
        
        # Add heatmap layer
        HeatMap(df_year[['Lat', 'Long']].values.tolist()).add_to(m)
        st.session_state.map = m
        
        return st.session_state.map
    else:
        st.error(f"No data available for year {df_year}")
        return pd.DataFrame()

def main():
    st.set_page_config(layout="wide")  # Use wide layout
    st.title("Crime Incidents Map")
    
    # Load data with caching
    with st.spinner('Loading data...'):
        df = load_data()
    
    try:
        # Get valid years (remove NaN values)
        valid_years = sorted(df['YEAR'].dropna().unique())
        
        if len(valid_years) > 0:
            
            selected_year = st.selectbox('Select Year', valid_years)
                
            # Filter data with caching
            df_year = filter_data(df, selected_year)
                
            # Display basic stats
            st.metric("Total Incidents", len(df_year))

           
            if len(df_year) > 0:
                with st.spinner("loading map... taking a second"):
                    crime_map = create_crime_map(df_year)
                    if crime_map is not None:
                        st_folium(
                            crime_map,
                            height=600,
                            width=None,
                            returned_objects=[]  # Disable return objects for better performance
                        )
        else:
            st.error("No valid years found in the data")
            
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
    


if __name__ == "__main__":
    main()