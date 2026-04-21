import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import seaborn as sns
import geopandas as gpd
import cartopy.crs as ccrs
from shapely import wkt
from matplotlib.ticker import FuncFormatter
from matplotlib.colors import TwoSlopeNorm
from mapclassify import NaturalBreaks

# Settings
np.random.seed(42)
FILE_PATH = './data/Fig03ab_dataset.csv'
WORLD_MAP_PATH = './data/world_map.shp'
MORP_RATIO_PATH = ./data/Fig03c_dataset.shp'

# 1. Data Loading and Preparation
df = pd.read_csv(FILE_PATH)
world_map = gpd.read_file(WORLD_MAP_PATH)

# Convert WKT strings to geometry and create GeoDataFrame
df['geometry'] = df['centroid'].apply(wkt.loads)
gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")

# Natural Breaks (Jenks) for Categorization
jenks = NaturalBreaks(y=df['TBE'].values, k=3)
thresholds = jenks.bins  # [low_threshold, moderate_high_threshold, max]
low_threshold = thresholds[0]
mod_high_threshold = thresholds[1]

# 2. Geographic Distribution Map
def lon_formatter(x, pos): return f"{abs(x):.0f}°{'W' if x < 0 else 'E'}"
def lat_formatter(y, pos): return f"{abs(y):.0f}°{'S' if y < 0 else 'N'}"

fig = plt.figure(figsize=(12, 10))
ax = plt.axes(projection=ccrs.PlateCarree())

# Plot base map
world_map.plot(color='#f0f0f0', ax=ax, edgecolor='None', transform=ccrs.PlateCarree())
ax.coastlines(linewidth=0.5)

# Colormap settings
vmax, vmin = 0.5, -0.5
norm = TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)
cmap = cm.get_cmap('coolwarm')

# Scatter plot
ax.scatter(gdf.geometry.x, gdf.geometry.y,
           c=df['TBE'], cmap=cmap, norm=norm,
           s=abs(gdf['TBE']) * 20,
           transform=ccrs.PlateCarree(), zorder=3)

# Axis formatting
ax.xaxis.set_major_formatter(FuncFormatter(lon_formatter))
ax.yaxis.set_major_formatter(FuncFormatter(lat_formatter))
ax.set_extent([-160, 180, -65, 80], crs=ccrs.PlateCarree())
ax.set_yticks([-30, 0, 30, 60], crs=ccrs.PlateCarree())
ax.set_xticks([-180, -120, -60, 0, 60, 120, 180], crs=ccrs.PlateCarree())

plt.tight_layout()
plt.show()

# 3. Violin Plot by Climate Zone
color_dict = {
    'Arid': '#F5D76E', 'Tropical': '#E97132',
    'Temperate': '#019E74', 'Cold': '#0072B2'
}

plt.figure(figsize=(3.7, 3.7))
ax_v = plt.gca()

# Highlight High TBE zone
ax_v.axhspan(mod_high_threshold, 5, facecolor='#d7191c', alpha=0.1)

# Plot Violin
sns.violinplot(x='Climate', y='TBE', data=df, palette=color_dict,
               order=['Arid', 'Tropical', 'Temperate', 'Cold'], ax=ax_v)

# Threshold lines
ax_v.axhline(y=low_threshold, color='grey', linestyle='--', linewidth=1)
ax_v.axhline(y=mod_high_threshold, color='grey', linestyle='--', linewidth=1)

ax_v.set_ylim([-0.9, 2.4])
ax_v.set_ylabel('TBE')
ax_v.set_xlabel('')
sns.despine()
plt.tight_layout()
plt.show()

# 4. Stacked Bar Plot for Morphology Ratios
morp_colors = [
    [165/255, 0/255, 38/255], [215/255, 48/255, 39/255],
    [244/255, 109/255, 67/255], [253/255, 174/255, 97/255],
    [254/255, 214/255, 51/255], [255/255, 235/255, 153/255]
]

built_up_df = pd.read_csv(MORP_RATIO_PATH)
climate_zones = ['Arid', 'Tropical', 'Temperate', 'Cold']
categories = ['Low', 'High']

fig, axes = plt.subplots(1, len(climate_zones), figsize=(7, 4), sharey=True)

for idx, climate in enumerate(climate_zones):
    ax_curr = axes[idx]
    subset = built_up_df[built_up_df['Climate'] == climate]
    
    # Calculate means for numeric columns grouped by Category
    numeric_cols = subset.select_dtypes(include='number').columns
    cat_means = subset.groupby('Category')[numeric_cols].mean().reindex(categories)

    # Plot stacked bars
    bottom_val = np.zeros(len(categories))
    for i, col in enumerate(cat_means.columns):
        ax_curr.bar(categories, cat_means[col], bottom=bottom_val, 
                    color=morp_colors[i], label=col if idx == 0 else "")
        bottom_val += cat_means[col].values

    ax_curr.set_title(climate)
    if idx == 0: ax_curr.set_ylabel('Proportion (%)')

plt.tight_layout()
plt.show()