import pandas as pd

def process_csv(input_file, output_file, header, delimiter='\t', skip_rows=14):
    # Read the CSV file into a DataFrame, skipping the first 14 rows
    df = pd.read_csv(input_file, delimiter=delimiter, skiprows=skip_rows)

    # Add the specified header
    df.columns = header

    # Write the DataFrame to a new CSV file
    df.to_csv(output_file, index=False, sep=delimiter)

# Specify your input and output file paths
input_file_path = './files/brainflow.csv'
output_file_path = './files/output5.csv'

# Specify the header for the columns
column_header = ['Sample Index', 'EXG Channel 0', 'EXG Channel 1', 'EXG Channel 2', 'EXG Channel 3', 'Accel Channel 0', 'Accel Channel 1', 'Accel Channel 2', 'Other', 'Other', 'Other', 'Other', 'Other', 'Timestamp', 'Other', 'Timestamp (Formatted)']

# Process the CSV file with tab as the delimiter using pandas
process_csv(input_file_path, output_file_path, column_header)

print(f"Processing completed. Output saved to {output_file_path}")
