import os
import shutil
from paddleocr import PaddleOCR

input_dir = os.getenv("CLASSIFY_INPUT_DIR", "/Users/aryan/Desktop/moondream-variphi/ANPR_pipeline/extracted_all_cropped_images")
bad_folder = os.getenv("BAD_DIR", "/Users/aryan/Desktop/moondream-variphi/ANPR_pipeline/bad_folder")
clean_data_folder = os.getenv("CLEAN_DIR", "/Users/aryan/Desktop/moondream-variphi/ANPR_pipeline/clean_data")

os.makedirs(bad_folder, exist_ok=True)
os.makedirs(clean_data_folder, exist_ok=True)

ocr = PaddleOCR(
    text_detection_model_name="PP-OCRv5_mobile_det",
    text_recognition_model_name="PP-OCRv5_mobile_rec",
    ocr_version="PP-OCRv5",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
) # Switch to PP-OCRv5_mobile models

image_files = [f for f in os.listdir(input_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]

for filename in image_files:
    image_path = os.path.join(input_dir, filename)
    try:
        result = ocr.predict(image_path)
        avg_threshold = 0
        if result and result[0] and "rec_scores" in result[0]:
            rec_scores = result[0]["rec_scores"]
            if len(rec_scores) > 0:
                avg_threshold = sum(rec_scores) / len(rec_scores)

        if avg_threshold < 0.75:
            shutil.move(image_path, os.path.join(bad_folder, filename))
            print(f"Moved {filename} to {bad_folder} (Average threshold: {avg_threshold:.2f})")
        else:
            shutil.move(image_path, os.path.join(clean_data_folder, filename))
            print(f"Moved {filename} to {clean_data_folder} (Average threshold: {avg_threshold:.2f})")

    except Exception as e:
        print(f"Error processing {filename}: {e}. Skipping.")
        # Optionally move errored files to a separate folder
        # shutil.move(image_path, os.path.join("/content/error_folder", filename))

print("Processing complete.")