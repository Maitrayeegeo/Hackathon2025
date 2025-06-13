import pandas as pd
import os

def create_inversion_data_files_from_single_csv(input_csv_path, output_directory):
    """
    Reads a CSV with X, Y, Topography, Grav (mGal), and Mag (nT) columns,
    and creates Tomofast-x-compliant files with SI units (m/s² and Tesla).
    """
    try:
        df = pd.read_csv(input_csv_path)

        # Check required columns
        required_columns = ['X', 'Y', 'Topography', 'Grav', 'Mag']
        if not all(col in df.columns for col in required_columns):
            raise KeyError(f"Missing columns. Expected: {required_columns}")

        # Convert units
        df['Z_Tomofast'] = -df['Topography']                # Z-positive-down
        df['Grav_SI'] = df['Grav'] * 1e-5                   # mGal → m/s²
        df['Mag_SI'] = df['Mag'] * 1e-9                     # nT → Tesla

        num_data_points = len(df)

        # --- Save gravity_data.txt (X Y Z Gravity) ---
        gravity_output_path = os.path.join(output_directory, "gravity_data.txt")
        with open(gravity_output_path, 'w') as f:
            f.write(f"{num_data_points}\n")
            for _, row in df.iterrows():
                f.write(f"{row['X']} {row['Y']} {row['Z_Tomofast']} {row['Grav_SI']}\n")

        # --- Save magnetic_data.txt (X Y Z Magnetics) ---
        magnetic_output_path = os.path.join(output_directory, "magnetic_data.txt")
        with open(magnetic_output_path, 'w') as f:
            f.write(f"{num_data_points}\n")
            for _, row in df.iterrows():
                f.write(f"{row['X']} {row['Y']} {row['Z_Tomofast']} {row['Mag_SI']}\n")

        print(f"Files saved to: {output_directory}")
        print(f"Data points: {num_data_points}")
        print(f"Add to .par file:\nforward.data.grav.nData = {num_data_points}\nforward.data.magn.nData = {num_data_points}")

    except FileNotFoundError:
        print(f"Error: Input file not found at {input_csv_path}")
    except KeyError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    input_csv = r"F:\Hackathon\Joint_Inversion\tomofast.csv"  # Update path
    output_dir = r"F:\Hackathon\Joint_Inversion\Tomofast_Processed_Data"
    os.makedirs(output_dir, exist_ok=True)
    create_inversion_data_files_from_single_csv(input_csv, output_dir)