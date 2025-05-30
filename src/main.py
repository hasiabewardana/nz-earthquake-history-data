# Data source
# http://wfs.geonet.org.nz/geonet/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=geonet:quake_search_v1&outputFormat=csv&cql_filter=origintime>='1900-01-01'+AND+origintime<'2025-05-31'

import geopandas as gpd
import pandas as pd

# Cleans GeoNet data.
df = pd.read_csv('data/original-source/earthquakes.csv', low_memory=False)
df = df[(df['eventtype'] == 'earthquake') & (df['origintime'] >= '1900-01-01') & (df['origintime'] <= '2025-05-31') & (
        df['magnitude'] >= 3)]
df = df[['latitude', 'longitude', 'magnitude', 'depth', 'origintime']]
df['origintime'] = pd.to_datetime(df['origintime'])  # Format dates
df.dropna(inplace=True)  # Remove missing values
df.to_csv('data/cleaned-earthquakes/cleaned_earthquakes.csv')

# Converts shapefile of NZ Regional Boundaries to GeoJSON.
gdf = gpd.read_file('data/regional-council-2022/regional-council-2022-clipped-generalised.shp')
gdf.set_crs(epsg=2193, inplace=True)  # Set original CRS
gdf = gdf.to_crs(epsg=4326)  # Convert to WGS84 for web maps
gdf.to_file('data/regional-council-2022/regional_council_2022.geojson', driver='GeoJSON')

# Converts cleaned earthquakes with regional boundaries to GeoJSON for Mapbox.
df = pd.read_csv('data/cleaned-earthquakes/cleaned_earthquakes.csv', low_memory=False)
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs="EPSG:4326")
boundary_gdf = gpd.read_file('data/regional-council-2022/regional_council_2022.geojson')
gdf = gpd.sjoin(gdf, boundary_gdf, how='left', predicate='within')
gdf.to_file('data/cleaned-earthquakes/cleaned_earthquakes.geojson', driver='GeoJSON')

# Filters major earthquakes.
df = pd.read_csv('data/cleaned-earthquakes/cleaned_earthquakes.csv', low_memory=False)
df = df[df['magnitude'] >= 7]
df.to_csv('data/major-earthquakes/major_earthquakes.csv')

# Converts major earthquakes to GeoJSON for Mapbox.
df = pd.read_csv('data/major-earthquakes/major_earthquakes.csv')
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude))
gdf.set_crs(epsg=4326, inplace=True)
gdf.to_file('data/major-earthquakes/major_earthquakes.geojson', driver='GeoJSON')

# Counts quake frequency.
df = pd.read_csv('data/cleaned-earthquakes/cleaned_earthquakes.csv')
df['origintime'] = pd.to_datetime(df['origintime'], errors='coerce')
df['year'] = df['origintime'].dt.year
freq = df.groupby('year').size()
freq.to_csv('data/quake-frequency/quake_frequency.csv')

# Finds quake clusters.
df = pd.read_csv('data/cleaned-earthquakes/cleaned_earthquakes.csv')
clusters = df.groupby(['latitude', 'longitude']).size().reset_index(name='count')
clusters.to_csv('data/quake-clusters/quake_clusters.csv')
