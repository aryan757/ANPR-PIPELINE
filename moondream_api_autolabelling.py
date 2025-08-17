import os
import csv
from PIL import Image
from transformers import AutoModelForCausalLM, AutoTokenizer # Assuming moondream is loaded with AutoModelForCausalLM

input_dir = os.getenv("MOON_INPUT_DIR", "/Users/aryan/Desktop/moondream-variphi/ANPR_pipeline/clean_data")
output_csv = os.getenv("MOON_OUTPUT_CSV", "/Users/aryan/Desktop/moondream-variphi/ANPR_pipeline/moondream.csv")


model = AutoModelForCausalLM.from_pretrained(
    "vikhyatk/moondream2",
    revision="2025-06-21",
    trust_remote_code=True,
    device_map={"": "cuda"}  # ...or 'mps', on Apple Silicon
)

image_files = [f for f in os.listdir(input_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]

with open(output_csv, 'w', newline='') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(['Filename', 'License Plate'])  # Write header

    for filename in image_files:
        image_path = os.path.join(input_dir, filename)
        try:
            image = Image.open(image_path).convert("RGB") # Ensure image is in RGB format

            # Query the moondream model for the license plate number
            object_query = model.query(image, "what is the indian license plate number ?")
            license_plate = object_query.get("answer", "N/A") # Get the answer or "N/A" if not found

            writer.writerow([filename, license_plate])
            print(f"Processed {filename}: {license_plate}")

        except Exception as e:
            print(f"Error processing {filename}: {e}. Skipping.")

print(f"Processing complete. Results saved to {output_csv}")