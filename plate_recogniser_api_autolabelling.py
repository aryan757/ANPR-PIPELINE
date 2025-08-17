import os
import requests
import csv
import time

input_dir = os.getenv("PLATE_INPUT_DIR", "/Users/aryan/Desktop/moondream-variphi/ANPR_pipeline/clean_data")
output_csv = os.getenv("PLATE_OUTPUT_CSV", "/Users/aryan/Desktop/moondream-variphi/ANPR_pipeline/Plate_recognisor_license_plate_results.csv")
regions = os.getenv("PLATE_REGIONS", "in").split(",")
api_token = os.getenv("PLATE_API_TOKEN", "13ef56e2cc75e26740f3dd82c55025284c097272")

image_files = [f for f in os.listdir(input_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]

with open(output_csv, 'w', newline='') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(['Filename', 'License Plate'])  # Write header

    for filename in image_files:
        image_path = os.path.join(input_dir, filename)
        try:
            with open(image_path, 'rb') as fp:
                response = requests.post(
                    'https://api.platerecognizer.com/v1/plate-reader/',
                    data=dict(regions=regions),
                    files=dict(upload=fp),
                    headers={'Authorization': f'Token {api_token}'})

            response_json = response.json()

            if response_json and "results" in response_json and len(response_json["results"]) > 0:
                license_plate = response_json["results"][0]["plate"]
                writer.writerow([filename, license_plate])
                print(f"Processed {filename}: {license_plate}")
            else:
                print(f"No license plate detected in {filename}. Skipping.")

        except Exception as e:
            print(f"Error processing {filename}: {e}. Skipping.")

        time.sleep(4) # Wait for 4 seconds

print(f"Processing complete. Results saved to {output_csv}")