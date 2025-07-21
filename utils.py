import os
import zipfile
import pandas as pd
import shutil
import time
from datetime import datetime

UPLOAD_DIR = "uploaded_files"
HISTORY_FILE = "file_history.csv"
MAX_SIZE_MB = 500

def ensure_dirs():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    if not os.path.exists(HISTORY_FILE):
        pd.DataFrame(columns=["filename", "timestamp", "size_mb", "note", "starred"]).to_csv(HISTORY_FILE, index=False)

def is_zip(file_path):
    return zipfile.is_zipfile(file_path)

def save_uploaded_file(file, note=""):
    ensure_dirs()
    file_path = os.path.join(UPLOAD_DIR, file.name)
    with open(file_path, "wb") as f:
        f.write(file.getbuffer())

    size_mb = round(len(file.getbuffer()) / (1024 * 1024), 2)
    if size_mb > MAX_SIZE_MB:
        os.remove(file_path)
        return f"File too large. Limit is {MAX_SIZE_MB}MB."

    if is_zip(file_path):
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            extract_path = os.path.join(UPLOAD_DIR, os.path.splitext(file.name)[0])
            zip_ref.extractall(extract_path)
            os.remove(file_path)
            csv_files = [f for f in os.listdir(extract_path) if f.endswith(".csv")]
            if len(csv_files) == 1:
                selected_csv = csv_files[0]
            else:
                selected_csv = csv_files[0] if csv_files else None

            _record_file_history(file.name, size_mb, note)
            return os.path.join(extract_path, selected_csv) if selected_csv else "No CSV found."

    _record_file_history(file.name, size_mb, note)
    return file_path

def _record_file_history(filename, size_mb, note=""):
    history = pd.read_csv(HISTORY_FILE)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entry = pd.DataFrame([{
        "filename": filename,
        "timestamp": timestamp,
        "size_mb": size_mb,
        "note": note,
        "starred": False
    }])
    updated = pd.concat([history, new_entry], ignore_index=True)
    updated.to_csv(HISTORY_FILE, index=False)

def get_file_history():
    ensure_dirs()
    history = pd.read_csv(HISTORY_FILE)
    history = history.sort_values(by="timestamp", ascending=False)
    history["timestamp"] = pd.to_datetime(history["timestamp"])
    thirty_days_ago = datetime.now() - pd.Timedelta(days=30)
    history = history[history["timestamp"] > thirty_days_ago]
    return history
