import json
import pandas as pd
import numpy as np
import os

def calculate_checksum(base_dir):
    # Load JSON file
    ocr_path = os.path.join(base_dir, "final_results.json")
    with open(ocr_path, "r") as file:
        final_results = json.load(file)

    # Extract table data
    table_data = final_results["page_1"]["table_result"]
    table = json.loads(table_data)
    df = pd.DataFrame(table)

    # Process columns containing transaction data
    data_columns = [col for col in df.columns if col.startswith("('Data',")]
    df_data = df[data_columns]
    df_data.columns = df_data.iloc[0]  # Set first row as column headers
    df_data = df_data.drop(0).reset_index(drop=True)

    # Replace missing values and convert columns to numeric
    df_data = df_data.replace({None: np.nan})
    df_data["WITHDRAWAL"] = pd.to_numeric(df_data["WITHDRAWAL"].str.replace(',', ''), errors='coerce')
    df_data["DEPOSIT"] = pd.to_numeric(df_data["DEPOSIT"].str.replace(',', ''), errors='coerce')
    df_data["BALANCE"] = pd.to_numeric(df_data["BALANCE"].str.replace(',', ''), errors='coerce')
    df_data = df_data.fillna(0)

    # Initialize variables
    withdrawal, deposit, balance = df_data["WITHDRAWAL"], df_data["DEPOSIT"], df_data["BALANCE"]
    prev_bal = balance.iloc[0]
    extracted_data = []

    # Row-wise checksum validation
    for index in range(df_data.shape[0]):
        if withdrawal[index] != 0:
            raw_bal = prev_bal - withdrawal[index]
        elif deposit[index] != 0:
            raw_bal = prev_bal + deposit[index]
        else:
            raw_bal = prev_bal

        raw_bal = round(raw_bal, 2)
        match = raw_bal == balance[index]

        # Save results to extracted_data
        extracted_data.append({
            "Row": index,
            "Previous Balance": prev_bal,
            "Withdrawal": withdrawal[index],
            "Deposit": deposit[index],
            "Calculated Balance": raw_bal,
            "Statement Balance": balance[index],
            "Match": bool(match)
        })

        # Update previous balance
        prev_bal = raw_bal

    # Save extracted data to new JSON file
    output_path = os.path.join(os.path.dirname(ocr_path), "checksum_results.json")
    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(extracted_data, output_file, ensure_ascii=False, indent=4)

    print(f"Extracted data saved to {output_path}")