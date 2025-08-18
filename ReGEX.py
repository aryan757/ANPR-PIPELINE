import pandas as pd
import re

# Load the merged CSV produced by the previous stage
df = pd.read_csv('merged_license_plate_results.csv')

# Comprehensive regex for Indian license plates
# Handles: CG07XX1234, CG 07 XX 1234, CG-07-XX-1234, etc.
indian_plate_regex = re.compile(r"^([A-Z]{2})\s?[-]?\s?(\d{2})\s?[-]?\s?([A-HJ-NP-Z]{1,2})\s?[-]?\s?(\d{1,4})$")

# Regex for Bharat series: 22 BH 1234 XX
bharat_regex = re.compile(r"^(\d{2})\s?BH\s?(\d{1,4})\s?([A-HJ-NP-Z]{1,2})$")

def clean_and_validate_plate(plate_str):
    if pd.isna(plate_str) or str(plate_str).strip() == '':
        return None

    plate = str(plate_str).upper().strip()
    # Remove unwanted characters but keep letters, numbers, spaces, and hyphens
    plate = re.sub(r'[^A-Z0-9\s\-]', '', plate)
    # Normalize multiple spaces to single space
    plate = re.sub(r'\s+', ' ', plate)

    # Check if it matches standard Indian format
    match = indian_plate_regex.match(plate)
    if match:
        state, rto, series, number = match.groups()
        return f"{state} {rto} {series} {number}"

    # Check if it matches Bharat series
    match = bharat_regex.match(plate)
    if match:
        year, number, letters = match.groups()
        return f"{year} BH {number} {letters}"

    return None

# Determine source columns dynamically to be resilient to naming
# Accept both "License_Plate_Source_1" and "License_Plate_Source1" styles
source_cols = []
for col in df.columns:
    if col.startswith('License_Plate_Source_') or col.startswith('License_Plate_Source'):
        if col != 'License_Plate_Source':  # avoid exact base name if present
            source_cols.append(col)

# Sort columns by any trailing integer to prioritize earlier sources
def _trailing_int(s: str) -> int:
    m = re.search(r"(\d+)$", s)
    return int(m.group(1)) if m else 9999

source_cols = sorted(source_cols, key=_trailing_int)

valid_plates = []
rejected_rows = []

for _, row in df.iterrows():
    plate_found = None

    for col in source_cols:
        candidate = row.get(col, None)
        validated = clean_and_validate_plate(candidate)
        if validated:
            plate_found = validated
            break

    if plate_found:
        valid_plates.append({
            'Filename': row.get('Filename'),
            'Corrected_License_Plate': plate_found
        })
    else:
        rejected_rows.append(row.to_dict())

valid_df = pd.DataFrame(valid_plates)
rejected_df = pd.DataFrame(rejected_rows)

print(f"Valid plates found: {len(valid_df)}")
print(f"Rejected rows: {len(rejected_df)}")

valid_df.to_csv('corrected_license_plates.csv', index=False)
rejected_df.to_csv('rejected_license_plates.csv', index=False)
