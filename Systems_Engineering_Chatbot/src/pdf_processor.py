import fitz  # PyMuPDF
import pandas as pd
import os

def extract_tables_from_pdf(pdf_path):
    """
    Extracts tables from a PDF file and returns them as a list of pandas DataFrames.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"The file {pdf_path} was not found.")

    doc = fitz.open(pdf_path)
    all_tables = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        tables = page.find_tables()
        if tables:
            for table in tables:
                # The extract method returns a list of lists.
                table_data = table.extract()
                if table_data:
                    # The first row is often the header.
                    header = table_data[0]
                    # The rest of the rows are the data.
                    data = table_data[1:]
                    # Create a pandas DataFrame.
                    df = pd.DataFrame(data, columns=header)
                    all_tables.append(df)

    return all_tables

if __name__ == '__main__':
    # Example usage:
    pdf_file = os.path.join(os.path.dirname(__file__), '..', 'Wach_PF_D_2023 (1).pdf')
    try:
        extracted_tables = extract_tables_from_pdf(pdf_file)
        if extracted_tables:
            print(f"Successfully extracted {len(extracted_tables)} tables.")
            # Print the first table as an example.
            print("\nFirst Table:")
            print(extracted_tables[0])
        else:
            print("No tables were found in the PDF.")
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"An error occurred: {e}")
