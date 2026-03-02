from datetime import datetime
import os 

def generate_log(data):
    """
    Generate a timestamped log file from a list of entries.

    - Validates that `data` is a list, raising ValueError otherwise.
    - Creates a file named log_YYYYMMDD.txt in the current directory.
    - Writes each list item on its own line, preserving order.
    - Prints a confirmation message including the filename.
    - Returns the filename.
    """
    # STEP 1: Validate input
    if not isinstance(data, list):
        raise ValueError("data must be a list")

    # STEP 2: Generate a filename with today's date (e.g., "log_20250408.txt")
    today = datetime.now().strftime("%Y%m%d")
    filename = f"log_{today}.txt"

    # STEP 3: Write the log entries to a file using File I/O
    with open(filename, "w") as file:
        for entry in data:
            file.write(f"{entry}\n")

    # STEP 4: Print a confirmation message with the filename
    print(f"Log written to {filename}")

    return filename
