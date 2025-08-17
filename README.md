## ANPR Pipeline

This pipeline crops license plates from images, classifies cropped images into clean vs. bad using OCR scores, runs three recognizers (Plate Recognizer API, Moondream, Qwen-VL), then sorts and merges their CSV outputs.

### Directory layout
- `image_cropping.py`: crops license plates
- `image_classifcation_good_bad.py`: splits images into `clean_data` and `bad_folder`
- `plate_recogniser_api_autolabelling.py`: calls Plate Recognizer API on clean images
- `moondream_api_autolabelling.py`: runs Moondream on clean images
- `Qwen_api_autolabelling.py`: runs Qwen-VL on bad images
- `Sort_the_csv.py`: sorts all CSVs
- `merge_the_csv.py`: merges the CSVs into one file
- `main.py`: orchestrates the full pipeline

### Setup
1. Python 3.10+
2. Install deps:
```bash
pip install -r /Users/aryan/Desktop/moondream-variphi/ANPR_pipeline/requirements.txt
```
3. Create a `.env` (see below) or pass flags when running `main.py`.

### Environment variables
You can override paths via env vars; `main.py` also accepts CLI flags.

- Cropping
  - `CROP_INPUT_DIR`: raw images directory
  - `CROP_OUTPUT_DIR`: cropped images directory

- Classification
  - `CLASSIFY_INPUT_DIR`: cropped images directory
  - `CLEAN_DIR`: output clean images directory
  - `BAD_DIR`: output bad images directory

- Plate Recognizer
  - `PLATE_INPUT_DIR`: input clean images directory
  - `PLATE_OUTPUT_CSV`: output CSV path (default `Plate_recognisor_license_plate_results.csv`)
  - `PLATE_API_TOKEN`: your Plate Recognizer API token
  - `PLATE_REGIONS`: comma-separated region codes (default `in`)

- Moondream
  - `MOON_INPUT_DIR`: input clean images directory
  - `MOON_OUTPUT_CSV`: output CSV path (default `moondream.csv`)

- Qwen-VL
  - `QWEN_INPUT_DIR`: input bad images directory
  - `QWEN_OUTPUT_CSV`: output CSV path (default `qwen_bad_license_plate_results.csv`)

### Run end-to-end
```bash
python3 /Users/aryan/Desktop/moondream-variphi/ANPR_pipeline/main.py \
  --raw-images-dir "/absolute/path/to/input_images" \
  --cropped-dir "/Users/aryan/Desktop/moondream-variphi/ANPR_pipeline/cropped_images" \
  --clean-dir "/Users/aryan/Desktop/moondream-variphi/ANPR_pipeline/clean_data" \
  --bad-dir "/Users/aryan/Desktop/moondream-variphi/ANPR_pipeline/bad_folder" \
  --plate-token YOUR_PLATE_RECOGNIZER_TOKEN \
  --plate-regions in
```

Outputs created in `ANPR_pipeline`:
- `Plate_recognisor_license_plate_results.csv`
- `moondream.csv`
- `qwen_bad_license_plate_results.csv`
- `merged_license_plate_results.csv`

### Notes
- Ensure you have CUDA or MPS if using GPU acceleration.
- Moondream and Qwen-VL will download models on first run.
- Plate Recognizer requires a valid API token.

### Using environment files
- Copy `example.env` to `.env` and update values:
```bash
cp /Users/aryan/Desktop/moondream-variphi/ANPR_pipeline/example.env /Users/aryan/Desktop/moondream-variphi/ANPR_pipeline/.env
```
- The orchestrator reads variables from the environment; export them or use `direnv`/`dotenv` if desired.

