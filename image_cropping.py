from transformers import AutoModelForCausalLM, AutoTokenizer
from PIL import Image
import os

model = AutoModelForCausalLM.from_pretrained(
    "vikhyatk/moondream2",
    revision="2025-06-21",
    trust_remote_code=True,
    device_map={"": "cuda"}  # ...or 'mps', on Apple Silicon
)

input_dir = os.getenv("CROP_INPUT_DIR", "/Users/aryan/Desktop/moondream-variphi/ANPR_pipeline/original_croppings")
output_dir = os.getenv("CROP_OUTPUT_DIR", "/Users/aryan/Desktop/moondream-variphi/ANPR_pipeline/cropped_images")
os.makedirs(output_dir, exist_ok=True)

image_files = [f for f in os.listdir(input_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]

for filename in image_files:
    image_path = os.path.join(input_dir, filename)
    output_path = os.path.join(output_dir, filename)

    try:
        image = Image.open(image_path)
        img_width, img_height = image.size

        objects = model.detect(image, "license plate")["objects"]

        if objects:
            # Assuming there's only one object (license plate)
            obj = objects[0]
            x_min, y_min, x_max, y_max = obj['x_min'], obj['y_min'], obj['x_max'], obj['y_max']

            # Convert normalized coordinates to pixel coordinates
            left = int(x_min * img_width)
            top = int(y_min * img_height)
            right = int(x_max * img_width)
            bottom = int(y_max * img_height)

            # Crop the image
            cropped_image = image.crop((left, top, right, bottom))

            # Save the cropped image
            cropped_image.save(output_path)
            print(f"Processed and saved cropped image for {filename}")
        else:
            print(f"No license plate detected in {filename}. Skipping.")

    except Exception as e:
        print(f"Error processing {filename}: {e}. Skipping.")

print("Processing complete.")