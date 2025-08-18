import argparse
import os
import subprocess
import sys


def run_step(title: str, script_path: str, env_overrides: dict | None = None) -> None:
    print(f"\n=== {title} ===")
    env = os.environ.copy()
    if env_overrides:
        env.update({k: str(v) for k, v in env_overrides.items() if v is not None})
    # Run each step from its script directory to ensure relative paths inside scripts work
    subprocess.run([sys.executable, script_path], check=True, env=env, cwd=os.path.dirname(script_path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ANPR pipeline end-to-end")
    parser.add_argument("--raw-images-dir", required=True, help="Folder containing the original images")
    parser.add_argument("--cropped-dir", required=True, help="Folder to save cropped images")
    parser.add_argument(
        "--clean-dir",
        default="/Users/aryan/Desktop/moondream-variphi/ANPR_pipeline/clean_data",
        help="Folder to save OCR-clean images",
    )
    parser.add_argument(
        "--bad-dir",
        default="/Users/aryan/Desktop/moondream-variphi/ANPR_pipeline/bad_folder",
        help="Folder to save low-quality images",
    )
    parser.add_argument("--plate-token", default=os.environ.get("PLATE_API_TOKEN", ""), help="Plate Recognizer API token")
    parser.add_argument("--plate-regions", default="in", help="Comma-separated regions code for Plate Recognizer")
    args = parser.parse_args()

    base_dir = "/Users/aryan/Desktop/moondream-variphi/ANPR_pipeline"

    # 1) Crop images
    run_step(
        "Cropping license plates",
        os.path.join(base_dir, "image_cropping.py"),
        {
            "CROP_INPUT_DIR": args.raw_images_dir,
            "CROP_OUTPUT_DIR": args.cropped_dir,
        },
    )

    # 2) Classify cropped images into clean_data and bad_folder
    run_step(
        "Classifying cropped images with OCR threshold",
        os.path.join(base_dir, "image_classifcation_good_bad.py"),
        {
            "CLASSIFY_INPUT_DIR": args.cropped_dir,
            "BAD_DIR": args.bad_dir,
            "CLEAN_DIR": args.clean_dir,
        },
    )

    # 3) Run Plate Recognizer on clean images
    run_step(
        "Running Plate Recognizer API",
        os.path.join(base_dir, "plate_recogniser_api_autolabelling.py"),
        {
            "PLATE_INPUT_DIR": args.clean_dir,
            "PLATE_OUTPUT_CSV": os.path.join(base_dir, "Plate_recognisor_license_plate_results.csv"),
            "PLATE_API_TOKEN": args.plate_token,
            "PLATE_REGIONS": args.plate_regions,
        },
    )

    # 4) Run Moondream on clean images
    run_step(
        "Running Moondream model",
        os.path.join(base_dir, "moondream_api_autolabelling.py"),
        {
            "MOON_INPUT_DIR": args.clean_dir,
            "MOON_OUTPUT_CSV": os.path.join(base_dir, "moondream.csv"),
        },
    )

    # 5) Run Qwen on bad images
    run_step(
        "Running Qwen-VL model",
        os.path.join(base_dir, "Qwen_api_autolabelling.py"),
        {
            "QWEN_INPUT_DIR": args.bad_dir,
            "QWEN_OUTPUT_CSV": os.path.join(base_dir, "qwen_bad_license_plate_results.csv"),
        },
    )

    # 6) Sort CSVs
    run_step("Sorting CSV files", os.path.join(base_dir, "Sort_the_csv.py"))

    # 7) Merge CSVs
    run_step("Merging CSV files", os.path.join(base_dir, "merge_the_csv.py"))

    # 8) Validate and normalize license plates using regex (final stage)
    run_step(
        "Validating and normalizing license plates (regex)",
        os.path.join(base_dir, "ReGEX.py"),
    )

    print("\nPipeline complete.")


if __name__ == "__main__":
    main()


