import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import seaborn as sns
import geopandas as gpd
import cartopy.crs as ccrs
from matplotlib.ticker import FuncFormatter
from matplotlib.colors import TwoSlopeNorm

# ==========================================
# 1. Configuration & Global Settings
# ==========================================
BASE_DIR = './data'
PATHS = {
    "world_map": os.path.join(BASE_DIR, './data/world_map.shp'),
    "tbe_spatial": os.path.join(BASE_DIR, './data/Fig04_data_delta_TBE_spatial_distribution.csv'),
    "driver_spatial": os.path.join(BASE_DIR, './data/Fig04_TBE_dominant_factor.csv'),
    "driver_bar": os.path.join(BASE_DIR, './data/Fig04_dominant_factor_divergence.csv'),
    "synergy_spatial": os.path.join(BASE_DIR, './data/Fig04_TBE_synergistic_effect.csv'),
    "synergy_bar": os.path.join(BASE_DIR, './data/Fig04_synergistic_effect_divergence.csv')
}

# Color Definitions
FACTOR_COLORS = {'Climate': '#1f77b4', 'Morphology': '#EF4E46', 'Comparable': 'black'}
SYNERGY_COLORS = {'Warming': "#d73027", 'Cooling': '#4575b4', 'Minimal': '#bdbdbd'}

def lon_formatter(x, pos): return f"{abs(x):.0f}°{'W' if x < 0 else 'E'}"
def lat_formatter(y, pos): return f"{abs(y):.0f}°{'S' if y < 0 else 'N'}"

# ==========================================
# 2. Map Plotting Function
# ==========================================
def create_base_map():
    fig = plt.figure(figsize=(12, 7))
    ax = plt.axes(projection=ccrs.PlateCarree())
    world_map = gpd.read_file(PATHS["world_map"])
    world_map.plot(color='#f0f0f0', ax=ax, edgecolor='None', transform=ccrs.PlateCarree())
    ax.coastlines(linewidth=0.5)
    
    ax.xaxis.set_major_formatter(FuncFormatter(lon_formatter))
    ax.yaxis.set_major_formatter(FuncFormatter(lat_formatter))
    ax.set_extent([-160, 180, -65, 80], crs=ccrs.PlateCarree())
    ax.set_yticks([-30, 0, 30, 60], crs=ccrs.PlateCarree())
    ax.set_xticks([-180, -120, -60, 0, 60, 120, 180], crs=ccrs.PlateCarree())
    return fig, ax

# ==========================================
# 3. Geographic Distributions
# ==========================================

# A. ΔTBE Spatial Distribution
df_tbe = pd.read_csv(PATHS["tbe_spatial"])
fig, ax = create_base_map()
norm = TwoSlopeNorm(vmin=-0.5, vcenter=0, vmax=0.5)
ax.scatter(df_tbe['lon'], df_tbe['lat'], c=df_tbe['delta_TBE'], 
           s=np.clip(np.abs(df_tbe['delta_TBE']) * 30, 8, 150),
           cmap='coolwarm', norm=norm, transform=ccrs.PlateCarree())
plt.title("Spatial Distribution of ΔTBE")
plt.show()

# B. Dominant Driver Spatial Distribution
df_driver = pd.read_csv(PATHS["driver_spatial"])
fig, ax = create_base_map()
for factor, color in FACTOR_COLORS.items():
    subset = df_driver[df_driver['dominant_factor'] == factor]
    ax.scatter(subset['lon'], subset['lat'], c=color, s=8, label=factor, transform=ccrs.PlateCarree())
plt.legend(loc='lower left')
plt.title("Dominant Drivers")
plt.show()

# C. Synergistic Effect Spatial Distribution
df_synergy = pd.read_csv(PATHS["synergy_spatial"])
fig, ax = create_base_map()
for cls in ['Warming', 'Cooling', 'Minimal']:
    subset = df_synergy[df_synergy['synergistic_effect'] == cls]
    ax.scatter(subset['lon'], subset['lat'], c=SYNERGY_COLORS[cls], s=10, label=cls, transform=ccrs.PlateCarree())
plt.legend(loc='lower left')
plt.title("Synergistic Effects")
plt.show()

# ==========================================
# 4. Diverging Bar Charts (By Region)
# ==========================================

def plot_diverging_bars(df, category_col, sign_col, color_dict, factors, title_prefix=""):
    for region in df['Global_Gro'].dropna().unique():
        fig, ax = plt.subplots(figsize=(6, 2.2))
        for f in factors:
            # Positive Change (Right side, dark)
            inc = df.loc[(df['Global_Gro'] == region) & (df[category_col] == f) & (df[sign_col] == 1), 'Percentage']
            inc_val = inc.values[0] if not inc.empty else 0
            
            # Negative Change (Left side, light)
            dec = df.loc[(df['Global_Gro'] == region) & (df[category_col] == f) & (df[sign_col] == -1), 'Percentage']
            dec_val = dec.values[0] if not dec.empty else 0

            ax.barh(f, inc_val, color=color_dict[f], alpha=0.85)
            ax.barh(f, -dec_val, color=color_dict[f], alpha=0.35)

            if inc_val > 0:
                ax.text(inc_val + 1, f, f"{inc_val:.1f}%", va='center', ha='left', fontsize=9)
            if dec_val > 0:
                ax.text(-dec_val - 1, f, f"{dec_val:.1f}%", va='center', ha='right', fontsize=9)

        ax.set_title(f"{region} - {title_prefix}")
        ax.set_xlabel("Percentage of Cities (%)")
        ax.axvline(0, color='black', linewidth=0.8)
        ax.set_xlim(-80, 80)
        plt.tight_layout()
        plt.show()

# Plot Diverging Bars for Drivers
df_driver_bar = pd.read_csv(PATHS["driver_bar"])
plot_diverging_bars(df_driver_bar, 'dominant_factor', 'dominant_sign', 
                    FACTOR_COLORS, ['Climate', 'Comparable', 'Morphology'], "Drivers")

# Plot Diverging Bars for Synergy
df_synergy_bar = pd.read_csv(PATHS["synergy_bar"])
plot_diverging_bars(df_synergy_bar, 'synergistic_effect', 'synergistic_sign', 
                    SYNERGY_COLORS, ['Cooling', 'Minimal', 'Warming'], "Synergy")