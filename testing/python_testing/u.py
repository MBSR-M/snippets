import zipfile
import os


def extract_whl(whl_path, extract_to):
    """Extracts all files from a .whl package into a specified folder."""
    try:
        if not os.path.exists(extract_to):
            os.makedirs(extract_to)  # Create the folder if it doesn't exist

        with zipfile.ZipFile(whl_path, 'r') as whl:
            whl.extractall(extract_to)
            print(f"Extracted all files to: {extract_to}")
    except zipfile.BadZipFile:
        print("Error: The file is not a valid .whl package.")
    except FileNotFoundError:
        print("Error: File not found.")


if __name__ == "__main__":
    whl_path = r"C:\Users\MustafaMubashir\Downloads\ca-67216-py2.py3-none-any (1).whl"
    extract_to = r"C:\Users\MustafaMubashir\Downloads\whl_extracted"

    extract_whl(whl_path, extract_to)
