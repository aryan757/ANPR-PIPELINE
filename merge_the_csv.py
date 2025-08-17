import os
import pandas as pd

csv_files = [
    "/Users/aryan/Desktop/moondream-variphi/ANPR_pipeline/Plate_recognisor_license_plate_results.csv",
    "/Users/aryan/Desktop/moondream-variphi/ANPR_pipeline/moondream.csv",
    "/Users/aryan/Desktop/moondream-variphi/ANPR_pipeline/qwen_license_plate_results.csv",
    "/Users/aryan/Desktop/moondream-variphi/ANPR_pipeline/qwen_bad_license_plate_results.csv",
]

output_csv = "/Users/aryan/Desktop/moondream-variphi/ANPR_pipeline/merged_license_plate_results.csv"

merged_df = None

for i, csv_file in enumerate(csv_files):
    try:
        if not os.path.exists(csv_file):
            print(f"Error: {csv_file} not found. Skipping.")
            continue

        df = pd.read_csv(csv_file)

        # Determine the correct license plate column name
        license_plate_col = None
        if 'License Plate' in df.columns:
            license_plate_col = 'License Plate'
        elif 'License Plate(results)' in df.columns:
            license_plate_col = 'License Plate(results)'
        else:
            print(f"Warning: Could not find a license plate column in {csv_file}. Skipping.")
            continue

        # Select only the 'Filename' and the identified license plate column
        df_to_merge = df[['Filename', license_plate_col]].copy()

        # Rename the license plate column for merging
        new_col_name = f"License_Plate_Source_{i+1}"
        df_to_merge.rename(columns={license_plate_col: new_col_name}, inplace=True)

        if merged_df is None:
            merged_df = df_to_merge
        else:
            merged_df = pd.merge(merged_df, df_to_merge, on='Filename', how='outer')

    except Exception as e:
        print(f"An error occurred while processing {csv_file}: {e}")

if merged_df is not None:
    merged_df.to_csv(output_csv, index=False)
    print(f"Merged {len(csv_files)} files. Saved to: {output_csv}")
else:
    print("No data was merged.")