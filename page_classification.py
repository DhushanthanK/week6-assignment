import os
import json
from paddleocr import PaddleOCR
from fuzzywuzzy import fuzz

# Define the keywords for each category along with the threshold for classification
categories = {
    "Bank Statement": {
        "keywords": [
            "Balance on June 1",
            "Balance on June 30",
            "Previous Balance",
            "Ending Balance",
            "total money out",
            "Total money in",
            "Statement Period",
            "Account Summary",
            "Discription",
            "withdrawal",
            "deposit",
            "Balance",
        ],
        "threshold": 75,
    },
    "Cheque": {
        "keywords": [
            "Pay",
            "A/c Payee",
            "Cheque",
            "Please sign above",
        ],
        "threshold": 75,
    },
    "Salary Slip": {
        "keywords": [
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
        ],
        "threshold": 75,
    },
    "Utility Bill": {
        "keywords": [
            "Billig Address",
            "Bill Amount",
            "Pay by date",
            "Bill Group",
            "Power Factor",
            "Supply address",
            "Bill No",
            "CA No",
            "Tariff Category",
            "MDI REading",
            "Bill No",
            "Bill Cycle",
            "Bill Date",
        ],
        "threshold": 75,
    },
}


def classify_text(text):
    """Classifies the text based on predefined categories using fuzzy matching and returns a score."""
    classified_results = {}

    # Convert text to lowercase for case-insensitive matching
    text_lower = text.lower()

    # Check each category for keywords
    for category, details in categories.items():
        matched_keywords = []
        total_score = 0

        for keyword in details["keywords"]:
            # Calculate the fuzzy match score
            score = fuzz.partial_ratio(keyword.lower(), text_lower)

            # Check if the score meets the threshold
            if score >= details["threshold"]:
                matched_keywords.append(keyword)
                total_score += score  # Accumulate scores for matched keywords

        # Store results if any keywords are matched
        if matched_keywords:
            average_score = total_score / len(
                matched_keywords
            )  # Calculate average score
            classified_results[category] = {
                "matched_keywords": matched_keywords,
                "average_score": average_score,
            }

    return classified_results


def classify_images(pdf_dir_path):
    """Extracts text from images in the given directory and classifies them based on thresholds."""
    ocr = PaddleOCR(use_angle_cls=True, lang="en")

    # Dictionary to hold classification results for each image
    classification_results = {}

    # Loop through all images in the directory
    for filename in sorted(os.listdir(pdf_dir_path)):
        if filename.endswith(".png"):  # Adjust according to your image file format
            image_path = os.path.join(pdf_dir_path, filename)

            # Extract OCR result from the image
            ocr_result = ocr.ocr(image_path, cls=True)

            # Concatenate extracted text from all detected words
            extracted_text = " ".join(
                [line[1][0] for result in ocr_result for line in result]
            )

            # Classify the extracted text
            classification = classify_text(extracted_text)

            # Store the classification results
            page_num = os.path.splitext(filename)[0].split("_")[
                -1
            ]  # Get page number from filename
            classification_results[f"page_{page_num}"] = classification

    print(f"classification results is {classification_results}")
    # Save the classification results to a JSON file
    json_path = os.path.join(pdf_dir_path, "classification_results.json")
    with open(json_path, "w", encoding="utf-8") as json_file:
        json.dump(classification_results, json_file, ensure_ascii=False, indent=4)

    return classification_results
