import numpy as np
import pandas as pd
import os
from scipy.interpolate import NearestNDInterpolator
import matplotlib.pyplot as plt

def create_model_grid(csv_file, dx=1000, dy=1000, dz=100, depth_below_topography=2000,
                     output_file="model_grid.txt", plot_cross_section=True):
    
   
    df = pd.read_csv(csv_file)
    x = df.iloc[:,0].values
    y = df.iloc[:,1].values
    topography_elevation = df.iloc[:,2].values  
    
    
    max_topography = np.max(topography_elevation)
    min_topography = np.min(topography_elevation)
    normalized_topography = topography_elevation - max_topography

    
    total_depth = depth_below_topography 
    dz_list = [dz] * int(np.ceil(total_depth / dz))
    nz = int(np.ceil(total_depth / dz))
    cumulative_depths = np.cumsum([0] + dz_list[:-1])

    
    x_unique = np.sort(np.unique(x))
    y_unique = np.sort(np.unique(y))
    
    
    x_edges = np.concatenate(([x_unique[0] - dx/2], 
                              x_unique[:-1] + dx/2, 
                              [x_unique[-1] + dx/2]))
    y_edges = np.concatenate(([y_unique[0] - dy/2], 
                              y_unique[:-1] + dy/2, 
                              [y_unique[-1] + dy/2]))

    nx = len(x_unique)
    ny = len(y_unique)

    
    topo_interp = NearestNDInterpolator(list(zip(x, y)), normalized_topography)
    
    print(f"Calculated nx: {nx}, ny: {ny}, nz: {nz}")
    print(f"Expected total elements (nx*ny*nz): {nx * ny * nz}")
    
    model_cells = []

    with open(output_file, 'w') as f:
        f.write(f"{nx * ny * nz}\n") 
        
        for k in range(nz): 
            for j in range(ny): 
                for i in range(nx): 
                    
                    
                    center_x = (x_edges[i] + x_edges[i+1]) / 2
                    center_y = (y_edges[j] + y_edges[j+1]) / 2
                    
                    
                    z_surface = -topo_interp(center_x, center_y) 
                    
                    z_min = z_surface + cumulative_depths[k]
                    z_max = z_min + dz_list[k]
                    
                    
                    if z_min < z_surface - 1e-6: 
                        z_min = z_surface 
                    
                    
                    f.write(f"{x_edges[i]} {x_edges[i+1]} "
                            f"{y_edges[j]} {y_edges[j+1]} "
                            f"{z_min} {z_max} "
                            f"0.0 {i+1} {j+1} {k+1}\n")
                    
                    model_cells.append({
                        'x_min': x_edges[i], 'x_max': x_edges[i+1],
                        'y_min': y_edges[j], 'y_max': y_edges[j+1],
                        'z_top': z_min, 'z_bottom': z_max
                    })

    print(f"Model grid saved to {output_file}")

    
    if plot_cross_section:
        plt.figure(figsize=(12, 6))
        
       
        centers_x = (x_edges[:-1] + x_edges[1:]) / 2
        centers_y = (y_edges[:-1] + y_edges[1:]) / 2

       
        mid_y_idx = ny // 2
        
       
        plot_cells = [cell for cell in model_cells 
                      if cell['y_min'] <= centers_y[mid_y_idx] < cell['y_max']]

        for cell in plot_cells:
            plt.plot([cell['x_min'], cell['x_max']], [cell['z_top'], cell['z_top']], 'k-', lw=0.5)
            plt.plot([cell['x_min'], cell['x_max']], [cell['z_bottom'], cell['z_bottom']], 'k-', lw=0.5)
            plt.plot([cell['x_min'], cell['x_min']], [cell['z_top'], cell['z_bottom']], 'k-', lw=0.5)
            plt.plot([cell['x_max'], cell['x_max']], [cell['z_top'], cell['z_bottom']], 'k-', lw=0.5)
        
       
        y_center = centers_y[ny//2]
        slice_df = df[(df['Y'] >= y_center-dy/2) & (df['Y'] <= y_center+dy/2)]
        if not slice_df.empty:
            plt.plot(slice_df['X'], -(slice_df['Z'] - max_topography), 'r.', markersize=4, 
                    label='Normalized Topography (Z-down)')
        
        plt.xlabel("X coordinate (m)")
        plt.ylabel("Depth (m) - Positive Down")
        plt.title(f"Model Cross-Section (Y ≈ {y_center:.0f}m)\n"
                 f"Cell Size: ~{dx}x{dy}x{dz}m, Depth Below Topo: {depth_below_topography}m")
        plt.gca().invert_yaxis()
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    
    csv_path = r"F:\Hackathon\Joint_Inversion\Tomofast_1.csv"
    output_dir = r"F:\Hackathon\Joint_Inversion\Tomofast_Processed_Data"
    os.makedirs(output_dir, exist_ok=True)

    output_model_grid_file = os.path.join(output_dir, "model_grid.txt")

    create_model_grid(csv_path,
                      dx=1000,
                      dy=1000,
                      dz=100,
                      depth_below_topography=2000,
                      output_file=output_model_grid_file,
                      plot_cross_section=True)