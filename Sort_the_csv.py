import pandas as pd

csv_files = [
    "/Users/aryan/Desktop/moondream-variphi/ANPR_pipeline/Plate_recognisor_license_plate_results.csv",
    "/Users/aryan/Desktop/moondream-variphi/ANPR_pipeline/moondream.csv",
    "/Users/aryan/Desktop/moondream-variphi/ANPR_pipeline/qwen_license_plate_results.csv",
    "/Users/aryan/Desktop/moondream-variphi/ANPR_pipeline/qwen_bad_license_plate_results.csv",
]

for csv_file in csv_files:
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file)

        # Sort by 'Filename'
        if 'Filename' in df.columns:
            df = df.sort_values(by='Filename')

        # Normalize and uppercase license plate-like columns
        if 'License Plate' in df.columns:
            df['License Plate'] = df['License Plate'].astype(str).str.strip().str.upper()
        if 'License Plate(results)' in df.columns:
            df['License Plate(results)'] = df['License Plate(results)'].astype(str).str.strip().str.upper()

        # Save the modified DataFrame back to the same CSV file
        df.to_csv(csv_file, index=False)
        print(f"Processed and saved: {csv_file}")

    except FileNotFoundError:
        print(f"Error: {csv_file} not found.")
    except KeyError as e:
        print(f"Error processing {csv_file}: Missing expected column {e}")
    except Exception as e:
        print(f"An error occurred while processing {csv_file}: {e}")

## now merge the License plate columns of each .csv files
