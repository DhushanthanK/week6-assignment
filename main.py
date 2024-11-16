import pdf_to_images
import page_classification
import os
import argparse
import json
import key_value_extraction
import ocr_extraction
import table_extraction
import post_processing
import checksum

def check_pages(data):
    result = {}
    for page_key, page_value in data.items():
        if isinstance(page_value, dict) and page_value:
            result[page_key] = list(page_value.keys())
        else:
            result[page_key] = [] 

    return result

def is_bank_statement(base_dir):

    final_results_path = os.path.join(base_dir, "final_results.json")
    try:
        with open(final_results_path, "r") as file:
            final_results = json.load(file)
        
        for page_data in final_results.values():
            if "Classification" in page_data and "Bank Statement" in page_data["Classification"]:
                return True
    except FileNotFoundError:
        print("final_results.json not found. Skipping checksum calculation.")
    
    return False

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Arguments needed to extract pdf")
    parser.add_argument("pdf_path", type=str, help="Path to the pdf file to execute")

    args = parser.parse_args()
    pdf_path = args.pdf_path
    base_dir = os.path.splitext(pdf_path)[0]
    
    pdf_to_images.convert_to_images(pdf_path)
    ocr_path = os.path.join(base_dir, "ocr_results.json")
    ocr_extraction.extract_text_from_images(base_dir)
    classfication_result = page_classification.classify_images(base_dir)
    classification_keys = check_pages(classfication_result)
    key_value_results = key_value_extraction.extract_key_info_from_ocr_results(
        ocr_path, classification_keys
    )
    table_result = table_extraction.extract_tables_from_images(base_dir)

    post_processing.extract_combined_information(
        classfication_result, key_value_results, table_result, base_dir
    )

    if is_bank_statement(base_dir):
        checksum.calculate_checksum(base_dir)
    else:
        print("Checksum calculation skipped: No 'Bank Statement' found in page classification.")