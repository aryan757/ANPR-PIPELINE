import os
import csv
from PIL import Image
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
    "Qwen/Qwen2.5-VL-7B-Instruct", torch_dtype="auto", device_map="auto"
)

processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-7B-Instruct")

input_dir = os.getenv("QWEN_INPUT_DIR", "/Users/aryan/Desktop/moondream-variphi/ANPR_pipeline/bad_folder")
output_csv = os.getenv("QWEN_OUTPUT_CSV", "/Users/aryan/Desktop/moondream-variphi/ANPR_pipeline/qwen_bad_license_plate_results.csv")

image_files = [f for f in os.listdir(input_dir) if f.endswith((".png", ".jpg", ".jpeg"))]

with open(output_csv, "w", newline="") as outfile:
    writer = csv.writer(outfile)
    writer.writerow(["Filename", "License Plate"])  # Write header

    for filename in image_files:
        image_path = os.path.join(input_dir, filename)
        try:
            image = Image.open(image_path)

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": image},
                        {"type": "text", "text": "What is the license plate number in this image? Provide only the number."},
                    ],
                }
            ]

            text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

            inputs = processor(text=[text], images=[image], padding=True, return_tensors="pt")
            inputs = inputs.to("cuda")

            generated_ids = model.generate(**inputs, max_new_tokens=128)
            generated_ids_trimmed = [out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)]
            license_plate = processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )[0].strip()

            license_plate = (
                license_plate.replace('"', "").replace("'", "").replace("[", "").replace("]", "")
            )

            writer.writerow([filename, license_plate])
            print(f"Processed {filename}: {license_plate}")

        except Exception as e:
            print(f"Error processing {filename}: {e}. Skipping.")

print(f"Processing complete. Results saved to {output_csv}")