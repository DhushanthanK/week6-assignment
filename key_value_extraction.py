import spacy
import cv2
from paddleocr import PaddleOCR
from fuzzywuzzy import fuzz
import json
import os


def extract_row_lines(ocr_output, y_threshold=20, x_threshold=200):
    rows = []
    current_row = []
    row_center = 0
    last_x = None

    for box in ocr_output:
        top_left_x = box[0][0][0]
        top_left_y = box[0][0][1]
        bottom_left_y = box[0][3][1]
        cell_center_y = (top_left_y + bottom_left_y) / 2

        if row_center == 0:
            row_center = cell_center_y

        if abs(row_center - cell_center_y) > y_threshold:
            if current_row:
                rows.append(current_row)
            row_center = cell_center_y
            current_row = [box[1][0]]
            last_x = top_left_x
        else:

            if last_x is not None and abs(top_left_x - last_x) > x_threshold:
                rows.append(current_row)
                current_row = [box[1][0]]
            else:
                current_row.append(box[1][0])

            last_x = top_left_x

    if current_row:
        rows.append(current_row)

    flattened_rows = [' '.join(row) for row in rows]
    return flattened_rows


def extract_key_value_pairs_fuzzy(lines, keys, threshold=80):
    key_value_pairs = {}

    for line in lines:
        # Ensure line is a string before applying fuzzy matching
        line = ' '.join(line) if isinstance(line, list) else line

        for key in keys:
            match_ratio = fuzz.partial_ratio(key.lower(), line.lower())

            if match_ratio >= threshold:
                key_index = line.lower().find(key.lower())

                if key_index != -1:
                    value_before_key = line[:key_index].strip()
                    value_after_key = line[key_index + len(key):].strip()

                    value = f"{value_before_key} {value_after_key}".strip()
                    key_value_pairs[key] = value

                keys.remove(key)  
                break 

    return key_value_pairs

def extract_key_info_from_ocr_results(ocr_results_path, classification_result):
    keys_bank_statement = [
            "Account Name",
            "Account Number",
            "Account Type",
            "Statement Period",
            "Balance on June 1",
            "Balance on June 30",
            "total money out",
            "Total money in",
    ]
    keys_Cheque = [
            "Pay",
            "RUPEES",
            "Prefix",
            "A/c No.",
    ]
    keys_Salary_Slip = [
            "Employee Name",
            "Designation",
            "Department",
            "Date of Joining",
            "ESI Number",
            "Employee ID",
            "PF No",
            "UAN",
            "Work Location",
            "LOP Days",
            "Worked Days",
            "Bank A/c No",
            "Basic",
            "HRA",
            "Conveyance Allowance",
            "Medical Allowance",
            "LTA",
            "Special Allowance",
            "Net Pay",
            "Ammont in Words",
            "Mode of Payment",
            "Total Net Payable ",
    ]
    keys_Utility =  [
            "Name",
            "Billing Address",
            "Code",
            "Supply address",
            "Bill Amount",
            "Pay By Date",
            "Bill Group",
            "Consumer No",
            "MRB / Page / Serial",
            "Bill No",
            "Bill Cycle",
            "K. No",
            "Energisation Date",
            "CA No",
            "Meter Serial No",
            "Supply/Con Type",
            "Bill No",
            "Bill Basis",
    ]

    # Load OCR results JSON
    with open(ocr_results_path, "r", encoding="utf-8") as file:
        ocr_results = json.load(file)

    # Dictionary to hold extracted key-value data
    extracted_data = {}

    # Process each page in OCR results
    for page_num, page_data in ocr_results.items():
        if classification_result[page_num] == ["Bank Statement"]:
            keys = keys_bank_statement
        elif classification_result[page_num] == ["Salary Slip"]:
            keys = keys_Salary_Slip
        elif classification_result[page_num] == ["Cheque"]:
            keys = keys_Cheque
        elif classification_result[page_num] == ["Utility"]:
            keys = keys_Utility
        else:
            keys = []

        # Extract rows from the OCR results using the extract_row_lines function
        rows = [
            line[1][0] for line in page_data[0]
        ]  # Adjust based on OCR output structure

        # Call extract_row_lines to organize rows based on bounding boxes
        row_lines = extract_row_lines(page_data[0])

        # Extract key-value pairs using fuzzy matching
        if keys == []:
            extracted_data[page_num] = {}
        else:
            page_extracted_data = extract_key_value_pairs_fuzzy(row_lines, keys)
            extracted_data[page_num] = page_extracted_data

    # Save extracted data to new JSON file
    output_path = os.path.join(
        os.path.dirname(ocr_results_path), "extracted_key_information.json"
    )
    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(extracted_data, output_file, ensure_ascii=False, indent=4)

    print(f"Extracted data saved to {output_path}")
    return extracted_data
