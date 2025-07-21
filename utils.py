import os
import zipfile
import pandas as pd
import shutil
import time
import csv
from datetime import datetime

# --- Configuration ---
UPLOAD_DIR = "uploaded_files"
HISTORY_FILE = "file_history.csv"
MAX_SIZE_MB = 500  # File size limit set to 500MB

def ensure_dirs():
    """Ensures that the necessary directories and history file exist."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    if not os.path.exists(HISTORY_FILE):
        # Create the history file with headers if it doesn't exist
        with open(HISTORY_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["filename", "timestamp", "size_mb", "note", "starred"])

def is_zip(file_path):
    """Checks if a file is a valid ZIP archive."""
    return zipfile.is_zipfile(file_path)

def _record_file_history(filename, size_mb, note=""):
    """
    Appends a new record to the history CSV file efficiently.
    Uses append mode to avoid reading the entire file on each write.
    """
    ensure_dirs()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entry = [filename, timestamp, size_mb, note, False]
    
    with open(HISTORY_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(new_entry)

def save_uploaded_file(file, note=""):
    """
    Saves an uploaded file, handles ZIP extraction, logs history, and checks size.

    Returns:
        - A string path to the processed CSV file.
        - An error message string if something goes wrong.
    """
    ensure_dirs()
    
    # --- Security Improvement: Sanitize filename ---
    # The import is moved inside the function and wrapped in a try/except
    # to prevent the app from crashing if werkzeug is not installed.
    try:
        from werkzeug.utils import secure_filename
        safe_filename = secure_filename(file.name)
    except ImportError:
        # Fallback if werkzeug is not installed. This makes it an optional dependency.
        print("Warning: werkzeug not found. Using basic filename sanitization. For better security, pip install werkzeug.")
        safe_filename = os.path.basename(file.name).replace("..", "").replace("/", "").replace("\\", "")

    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    # Write file to check its size
    file_buffer = file.getbuffer()
    with open(file_path, "wb") as f:
        f.write(file_buffer)

    size_mb = round(len(file_buffer) / (1024 * 1024), 2)
    if size_mb > MAX_SIZE_MB:
        os.remove(file_path) # Clean up the oversized file
        return f"File too large ({size_mb}MB). Limit is {MAX_SIZE_MB}MB."

    # --- ZIP File Handling Improvement ---
    if is_zip(file_path):
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                extract_path = os.path.join(UPLOAD_DIR, os.path.splitext(safe_filename)[0])
                zip_ref.extractall(extract_path)
                
                csv_files = [f for f in os.listdir(extract_path) if f.endswith(".csv")]

                if not csv_files:
                    shutil.rmtree(extract_path)
                    return "No CSV files found in the ZIP archive."
                
                # For now, we'll return the first one as per original logic.
                selected_csv_path = os.path.join(extract_path, csv_files[0])
                _record_file_history(file.name, size_mb, note)
                return selected_csv_path

        except zipfile.BadZipFile:
            return "Error: The uploaded file is not a valid ZIP archive."
        finally:
            # Clean up the original zip file after processing
            if os.path.exists(file_path):
                os.remove(file_path)
    
    # --- Standard File Handling (e.g., .csv) ---
    _record_file_history(file.name, size_mb, note)
    return file_path

def get_file_history():
    """
    Retrieves file upload history from the last 30 days.
    """
    ensure_dirs()
    try:
        history = pd.read_csv(HISTORY_FILE)
        if history.empty:
            return pd.DataFrame() # Return empty dataframe if no history
            
        history = history.sort_values(by="timestamp", ascending=False)
        history["timestamp"] = pd.to_datetime(history["timestamp"])
        
        # Filter for entries within the last 30 days
        thirty_days_ago = datetime.now() - pd.Timedelta(days=30)
        history = history[history["timestamp"] > thirty_days_ago]
        return history
    except pd.errors.EmptyDataError:
        # This can happen if the file exists but is empty
        return pd.DataFrame()
    except FileNotFoundError:
        return pd.DataFrame()
