import pandas as pd
import plotly.express as px


def generate_color_palette(n):
    # Use the qualitative color set from Plotly Express
    color_palette = px.colors.qualitative.Set1[:n]

    return color_palette


# Example usage: Generate a list of 5 colors
n_colors = 5
color_list = generate_color_palette(n_colors)

# Sample data with longitude, latitude, and labels
data = [
    {"lat": 37.7749, "lon": -122.4194, "label": "Point 1", "value": 3},
    {"lat": 34.0522, "lon": -118.2437, "label": "Point 2", "value": 5},
    {"lat": 40.7128, "lon": -74.0060, "label": "Point 3", "value": 2},
]

data = pd.DataFrame.from_dict(data)

fig = px.scatter_mapbox(
    data,
    lat="lat",
    lon="lon",
    hover_name="label",
    color="label",
    # color_continuous_scale=color_list,
    size_max=15,
    zoom=4,
)

fig.update_layout(mapbox_style="open-street-map")
fig.show()
