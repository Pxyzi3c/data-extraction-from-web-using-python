import sys
import json
import time
import logging
import schedule
import pandas as pd
from os import environ, remove
from pathlib import Path
from ftplib import FTP_TLS
from typing import Dict

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

CONFIG_PATH = Path("config.json")

def load_config(path: Path = CONFIG_PATH) -> Dict:
    with path.open("r") as fp:
        return json.load(fp)

def get_ftp() -> FTP_TLS:
    try:
        ftp = FTP_TLS(environ["FTPHOST"])
        ftp.login(environ["FTPUSER"], environ["FTPPASS"])
        ftp.prot_p()
        logging.info("Connected to FTP.")
        return ftp
    except Exception as e:
        logging.error(f"Failed to connect to FTP: {e}")
        raise

def read_csv_from_url(config: Dict) -> pd.DataFrame:
    return pd.read_csv(config["URL"], **config.get("PARAMS", {}))

def upload_file(ftp: FTP_TLS, file_path: Path):
    try:
        with file_path.open("rb") as fp:
            ftp.storbinary(f"STOR {file_path.name}", fp)
        logging.info(f"Uploaded {file_path.name} to FTP.")
    except Exception as e:
        logging.error(f"Failed to upload {file_path.name}: {e}")
        raise

def clean_up(file_path: Path):
    try:
        file_path.unlink()
        logging.info(f"Deleted {file_path.name}.")
    except Exception as e:
        logging.warning(f"Failed to delete {file_path.name}: {e}")

def process_source(source_name: str, config: Dict, ftp: FTP_TLS):
    file_path = Path(f"{source_name}.csv")
    try:
        df = read_csv_from_url(config)
        df.to_csv(file_path, index=False)
        logging.info(f"Saved {file_path.name}.")
        upload_file(ftp, file_path)
    finally:
        clean_up(file_path)

def run_pipeline():
    config = load_config()
    with get_ftp() as ftp:
        for source_name, source_config in config.items():
            process_source(source_name, source_config, ftp)

def main():
    if len(sys.argv) < 2:
        logging.error("Missing parameter: 'manual' or 'schedule'")
        sys.exit(1)

    mode = sys.argv[1].lower()

    if mode == "manual":
        run_pipeline()
    elif mode == "schedule":
        schedule.every().day.at("23:05").do(run_pipeline)
        logging.info("Scheduler started.")
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Scheduler stopped manually.")
    else:
        logging.error("Invalid parameter: use 'manual' or 'schedule'")

if __name__ == "__main__":
    main()