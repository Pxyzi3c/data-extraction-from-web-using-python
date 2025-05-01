import sys
import json
import time 
import schedule
import pandas as pd
from os import environ, remove
from pathlib import Path
from ftplib import FTP_TLS

def get_ftp() -> FTP_TLS:
    # Get FTP details
    FTPHOST = environ["FTPHOST"]
    FTPUSER = environ["FTPUSER"]
    FTPPASS = environ["FTPPASS"]

    # Return authenticated FTP
    ftp = FTP_TLS(FTPHOST, FTPUSER, FTPPASS)
    ftp.prot_p()
    return ftp

def upload_to_ftp(ftp: FTP_TLS, file_source: Path):
    with open(file_source, "rb") as fp:
        ftp.storbinary(f"STOR {file_source.name}", fp)

def read_csv(config: dict) -> pd.DataFrame:
	url = config["URL"]
	params = config["PARAMS"]
	return pd.read_csv(url, **params)

def pipeline():
    # Load source configuration
    with open("config.json", "rb") as fp:
        config = json.load(fp)
    
    ftp = get_ftp()

    # Loop through each configuration to get the source_name and its corresponding configuration
    for source_name, source_config in config.items():
        file_name = Path(f"{source_name}.CSV")
        df = read_csv(source_config)
        df.to_csv(file_name, index=False)
        print(f"File {file_name} downloaded")

        # Transfer to FTP
        upload_to_ftp(ftp, file_name)
        print(f"File {file_name} uploaded")
        remove(file_name)
        print(f"File {file_name} deleted")

if __name__=="__main__":
    param = sys.argv[1]

    if param.lower() == "manual":
         pipeline()
    elif param.lower() == "schedule":
        schedule.every().day.at("23:05").do(pipeline)
        while True:
            schedule.run_pending()
            time.sleep(1)
    else:
         print("Invalid parameter")