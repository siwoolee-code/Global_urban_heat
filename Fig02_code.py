import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import ast

file_path = './data/Fig02_data.csv'

# 1. Load data 
df = pd.read_csv(file_path)

# 2. Settings (Color and Order)
climate_order = ['Arid', 'Tropical', 'Temperate', 'Cold']
color_dict = {
    'Arid': '#F5D76E',
    'Tropical': '#E97132',
    'Temperate': '#019E74',
    'Cold': '#0072B2'
}
morp_labels = [f'Morp{i}' for i in range(1, 7)]
morp_indices = np.arange(len(morp_labels))
n_climates = len(climate_order)
total_width = 0.8 
width = total_width / n_climates 

# 3. Plotting
plt.figure(figsize=(13, 6))
ax = plt.gca()

for i, climate in enumerate(climate_order):
    # Filtering and sorting the relevant climate data in Morp order 
    stats = df[df['Climate_zone'] == climate].copy()
    stats['Surr_Morp'] = pd.Categorical(stats['Surr_Morp'], categories=morp_labels, ordered=True)
    stats = stats.sort_values('Surr_Morp')
    
    # x-axis position calculation (Dodge)
    pos = morp_indices + (i - (n_climates - 1) / 2) * width
    
    # (A) Bar Plot - mean values 
    ax.bar(pos, stats['changed_value'], width, 
           label=climate, color=color_dict[climate], zorder=2)
    
    # (B) Error Bars - std_value
    ax.errorbar(pos, stats['changed_value'], yerr=stats['std_value'],
                fmt='none', ecolor='black', elinewidth=1.2, capsize=3, alpha=0.7, zorder=5)
    
    # (C) Individual Points 
    for j, raw_str in enumerate(stats['changed_value_by_Center_Morp']):
        points = ast.literal_eval(raw_str)
        
        x_jitter = np.random.uniform(-width * 0.2, width * 0.2, len(points)) + pos[j]
        ax.scatter(x_jitter, points, 
                   s=12, color='black', alpha=0.45, 
                   edgecolors='white', linewidths=0.4, zorder=4)

# 4. Axis and styling
ax.set_xlabel('Surrounding Urban Structure (LCZ)', fontsize=13)
ax.set_ylabel('Surrounding Thermal Impact (K)', fontsize=13)
ax.set_xticks(morp_indices)
ax.set_xticklabels(morp_labels, rotation=0, fontsize=11)
ax.set_ylim([-0.3, 1.1])
ax.axhline(y=0, color='black', linewidth=0.8, zorder=1)

ax.legend(title='Climate Zone', frameon=False)

plt.tight_layout()


plt.show()



