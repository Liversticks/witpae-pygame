import pandas as pd
import sys

def extract_parentheses_value(file_name, source_col, target_col):
    """
    Reads a CSV, extracts values inside parentheses from a source column,
    and saves them into a new target column.
    """
    # 1. Load the dataset
    df = pd.read_csv(file_name)
    
    # 2. Extract value inside parentheses
    # regex explanation: \( matches '(', (.*?) captures the content, \) matches ')'
    df[target_col] = df[source_col].astype(str).str.extract(r'\((.*?)\)')

    # 3. Remove the parentheses and their contents from the source column
    # \s* matches any whitespace before the '(' to keep the column clean
    # \(.*?\) matches the parentheses and everything inside them
    df[source_col] = df[source_col].astype(str).str.replace(r'\s*\(.*?\)', '', regex=True)
    
    # 4. Save the modified file (optional) or return the dataframe
    df.to_csv(file_name, index=False)
    
    print(f"Extraction complete! New column '{target_col}' created.")
    print(f"File saved as: {file_name}")
    return df

# --- Example Usage ---
# Using the 'bases.csv' file you referenced:
# Let's extract the parenthesized value from 'Port' into a new column 'Port_Max'
if __name__ == "__main__":
    updated_df = extract_parentheses_value(sys.argv[1], sys.argv[2], sys.argv[3])

    # Displaying a preview
    print(updated_df[['Name', sys.argv[2], sys.argv[3]]].head())