# Intelligent Document Processing App for Financial Applications**

This project is an **end-to-end intelligent document processing application** designed specifically for financial documents. It automates the extraction, classification, and validation of information from financial PDFs, providing streamlined and accurate results for use in financial analysis.


## Workflow Overview

1. **Input**: A financial document in PDF format.

2. **OCR Process**:

Convert the PDF into page-wise images.

Extract text from each page using **PaddleOCR**.

3. **Classification**: Categorize each page based on its content.

4. **Key-Value Extraction**: Identify and extract relevant information from the document.

5. **Table Extraction**: Parse tabular data and save it in structured formats.

6. **Checksum Validation**: Recalculate balances from transaction rows and flag discrepancies.

7. **Output**: Save all results in individual JSON files for downstream use.


## JSON Outputs

1. **OCR Results**: `ocr_results.json`

Contains text extracted from each page.

2. **Classification Results**: `classification_results.json`

Categorizes pages with their corresponding labels.

3. **Key-Value Extraction**: `extracted_key_information.json`

Stores extracted details like account numbers, transaction dates, and other metadata.

4. **Table Extraction**: `all_extracted_tables.json` and `page_i_table.json`

Provides structured tabular data extracted from the document.

5. **Checksum Validation**: `checksum_results.json`

Includes validation results with calculated balances and mismatch flags.

6. **Final Results**: `final_results.json`

Includes classification results, key values, table results combined.


## Installation

**Prerequisites**

• Python 3.8 or later

• PaddleOCR

• Pandas

• NumPy

• PyTorch

•Other required libraries listed in requirements.txt


## Steps

1. Clone the repository:
```bash
git clone https://github.com/Dhushan27/week6-assignment.git
cd week6-assignment
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Run the app:
```bash
python main.py /path/to/financial-document.pdf
```


## Example JSON Output

**Checksum Results (**checksum_results.json**):**
```bash
[
    {
        "Row": 0,
        "Previous Balance": 1000.0,
        "Withdrawal": 200.0,
        "Deposit": 0.0,
        "Calculated Balance": 800.0,
        "Statement Balance": 800.0,
        "Match": true
    },
    {
        "Row": 1,
        "Previous Balance": 800.0,
        "Withdrawal": 0.0,
        "Deposit": 300.0,
        "Calculated Balance": 1100.0,
        "Statement Balance": 1100.0,
        "Match": true
    }
]
```
