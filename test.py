# Import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import networkx as nx
import os

# Step 1: Load Data
file_path = "H:\Cyber-crime-analysis\Cyber-crime-analysis\\notebooks\data\enriched_data.csv"  # Update this path if the file is stored elsewhere
# data = pd.read_excel(file_path, engine='openpyxl')
data = pd.read_csv(file_path)

# Step 2: Analyze and Visualize Data

# 2.1 Bar Chart: Most Common Operating Systems
plt.figure(figsize=(10, 6))
os_counts = data["os"].value_counts()
sns.barplot(x=os_counts.index, y=os_counts.values, palette="viridis")
plt.title("Most Common Operating Systems", fontsize=16)
plt.xlabel("Operating System", fontsize=12)
plt.ylabel("Count", fontsize=12)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("os_distribution.png")
plt.show()

# 2.2 Pie Chart: Device Types Distribution
device_type_counts = data["os"].value_counts()
plt.figure(figsize=(8, 8))
plt.pie(device_type_counts, labels=device_type_counts.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette("pastel"))
plt.title("Device Types Distribution", fontsize=16)
plt.savefig("device_type_distribution.png")
plt.show()

# 2.3 Heatmap: Correlation Between Numeric Features (if applicable)
# Assuming there are numeric columns such as screen resolution width/height
if "screen_width" in data.columns and "screen_height" in data.columns:
    data["screen_width"] = data["screen"].apply(lambda x: int(x.split("x")[0]) if pd.notnull(x) else None)
    data["screen_height"] = data["screen"].apply(lambda x: int(x.split("x")[1]) if pd.notnull(x) else None)

    numeric_features = data.select_dtypes(include=["number"])
    plt.figure(figsize=(10, 8))
    sns.heatmap(numeric_features.corr(), annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Correlation Between Numeric Features", fontsize=16)
    plt.tight_layout()
    plt.savefig("numeric_correlation_heatmap.png")
    plt.show()

# 2.4 Network Analysis: Highlight Most Connected Nodes
# Create a graph object
network_graph = nx.Graph()

# Add nodes and edges based on user-device relationships
for _, row in data.iterrows():
    network_graph.add_node(row["device_id"], label="Device", color="blue")
    network_graph.add_node(row["identity"], label="User", color="green")
    network_graph.add_edge(row["device_id"], row["identity"])  # Connect devices and users

# Calculate degree centrality
degree_centrality = nx.degree_centrality(network_graph)

# Highlight top 5 most connected nodes
top_nodes = sorted(degree_centrality, key=degree_centrality.get, reverse=True)[:5]

# Draw the network graph
pos = nx.spring_layout(network_graph)
node_colors = ["red" if node in top_nodes else "blue" for node in network_graph.nodes]
plt.figure(figsize=(12, 12))
nx.draw(network_graph, pos, with_labels=False, node_color=node_colors, node_size=50, edge_color="gray", alpha=0.7)
plt.title("Network Analysis: Most Connected Nodes Highlighted", fontsize=16)
plt.savefig("network_analysis_highlighted.png")
plt.show()

# 2.5 Geographical Analysis: IP Country Distribution Map
# Requires geopandas and a world shapefile
# try:
#     import geopandas as gpd
#     import geodatasets

#     # Get the path to the naturalearth_lowres dataset
#     dataset_path = geodatasets.get_path("naturalearth_lowres")
#     from shapely.geometry import Point
    
#     # Prepare geographical data
#     world = geodatasets.get_path('H:\Cyber-crime-analysis\Cyber-crime-analysis\data\\ne_110m_admin_0_countries\\ne_110m_admin_0_countries.shp')
#     country_counts = data["ip_country"].value_counts()

#     # Create DataFrame for mapping
#     map_data = pd.DataFrame({"country": country_counts.index, "count": country_counts.values})
#     map_data = map_data.merge(world, left_on="country", right_on="name", how="inner")
#     map_data = gpd.GeoDataFrame(map_data)

import pandas as pd
import geopandas as gpd
import geodatasets
import matplotlib.pyplot as plt

try:
    # Load the world dataset using geopandas
    # world = gpd.read_file(geodatasets.get_path("H:\Cyber-crime-analysis\Cyber-crime-analysis\data\\ne_110m_admin_0_countries\\ne_110m_admin_0_countries.shp"))
    world = gpd.read_file(r"H:\Cyber-crime-analysis\Cyber-crime-analysis\data\ne_110m_admin_0_countries\ne_110m_admin_0_countries.shp")
    # Example: Assuming 'data' is a pandas DataFrame with 'ip_country' column
    # Replace this with your actual DataFrame
    # data = pd.read_csv("your_data.csv")  # Load your data here

    # Verify country column
    if "country" not in data.columns:
        raise ValueError("Column 'country' not found in CSV. Available columns: " + str(data.columns))

    # Load the world dataset using geopandas' built-in dataset
    try:
        world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
    except Exception as e:
        # Fallback to local shapefile if built-in dataset fails
        shapefile_path = r"H:\Cyber-crime-analysis\Cyber-crime-analysis\data\ne_110m_admin_0_countries\ne_110m_admin_0_countries.shp"
        if not os.path.exists(shapefile_path):
            raise FileNotFoundError(f"Shapefile not found at {shapefile_path}. Download from https://www.naturalearthdata.com/downloads/110m-cultural-vectors/110m-admin-0-countries/")
        world = gpd.read_file(shapefile_path)

    # Get country counts
    country_counts = data["country"].value_counts()

    # Create DataFrame for mapping
    map_data = pd.DataFrame({"country": country_counts.index, "count": country_counts.values})

    # Standardize country names to match world dataset
    country_mapping = {
        "United States": "United States of America",
        "Russia": "Russia",
        "Ghana": "Ghana"
    }
    map_data["country"] = map_data["country"].map(country_mapping).fillna(map_data["country"])

    # Merge with world GeoDataFrame
    print("World columns:", world.columns)  # Debug: Check available columns
    map_data = world.merge(map_data, left_on="ADMIN", right_on="country", how="left")

    # Fill NaN values in 'count' with 0
    map_data["count"] = map_data["count"].fillna(0)

    # Ensure map_data is a GeoDataFrame
    map_data = gpd.GeoDataFrame(map_data, geometry="geometry")

    # Plot the map
    fig, ax = plt.subplots(figsize=(12, 8))
    map_data.plot(
        column="count",
        ax=ax,
        legend=True,
        cmap="OrRd",
        missing_kwds={"color": "lightgrey"},
        legend_kwds={"label": "Number of IPs", "orientation": "horizontal"}
    )
    ax.set_title("IP Distribution by Country")
    plt.show()


    # Plot map
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    world.plot(ax=ax, color="lightgrey")
    map_data.plot(column="count", ax=ax, legend=True, cmap="OrRd", legend_kwds={"shrink": 0.6})
    plt.title("IP Country Distribution", fontsize=16)
    plt.savefig("ip_country_distribution_map.png")
    plt.show()

except ImportError:
    print("To plot geographical data, install GeoPandas and dependencies.")

# Step 3: Summarize Insights
# Display basic statistics about the enriched data
print("Basic Statistics of Enriched Data:")
print(data.describe(include="all"))

# Save any additional outputs or logs
data.describe(include="all").to_csv("data_summary.csv")