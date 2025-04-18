# **Extracting Data from Web to FTP using Python**

This document provides a guide to setting up an environment and creating a Python data pipeline to extract data from a web source and transfer it to an FTP server.

## **Table of Contents**

1. [WSL Setup](#u5d6pakvsf4v)
2. [FTP Setup on Linux (WSL)](#5u21mkfklle3)
    - [Update Ubuntu](#qoqqk0e2an1y)
    - [Host FTP on Linux](#49wd03w6wlj3)
    - [Configure VSFTPD](#oj4ql9wum9dp)
    - [Create a New File for the List of Users with Chroot](#lriiztm3pyxs)
    - [Create an FTP User](#8894yebj4i6p)
    - [Test Connection](#c2umhzoy503h)
3. [Testing FTP Connection with Python](#bn7ee6600qo0)
4. [Setting Up Python Development Environment](#hudf6hjwqrjw)
    - [Initialization](#pridh4k6bwh0)
    - [Securing the Credentials](#cl60pvrbskxv)
5. [Creating Python Data Pipeline](#kewvqoipt9jz)

## **1\. WSL Setup**

This guide assumes you have the Windows Subsystem for Linux (WSL) installed and a Linux distribution (like Ubuntu) set up. If you haven't already, please refer to the official Microsoft documentation for instructions on how to install WSL.

## **2\. FTP Setup on Linux (WSL)**

This section details how to set up an FTP server on your Linux distribution within WSL.

### **Update Ubuntu**

First, ensure your Ubuntu system is up-to-date:

sudo apt update && sudo apt upgrade  

### **Host FTP on Linux**

Install the vsftpd package:

sudo apt install vsftpd  

### **Configure VSFTPD**

1. **Create a backup of the configuration file:**  
    sudo cp /etc/vsftpd.conf /etc/vsftpd.conf_original  

2. **Edit the vsftpd.conf file:**  
    sudo nano /etc/vsftpd.conf  

3. **Apply the following configurations (uncomment or add these lines):**  
    local_enable=YES  
    write_enable=YES  
    chroot_local_user=YES  
    chroot_list_enable=YES  
    chroot_list_file=/etc/vsftpd.chroot_list  
    ssl_enable=YES  
    require_ssl_reuse=NO  

4. **Restart the vsftpd service:**  
    sudo systemctl restart vsftpd  

5. **Check the status of the vsftpd service:**  
    sudo systemctl status vsftpd  

### **Create a New File for the List of Users with Chroot**

sudo touch /etc/vsftpd.chroot_list  

### **Create an FTP User**

1. **Add a new user named ftpuser (you can choose a different username):**  
    sudo adduser ftpuser  
    <br/>(You will be prompted to set a password for this user.)
2. **Create an FTP directory for the user:**  
    sudo mkdir /home/ftpuser/ftp  

3. **List the contents of the /home directory to verify the new folder:**  
    ls /home  

4. **Change the ownership of the new FTP directory:**  
    sudo chown nobody:nogroup /home/ftpuser/ftp  

5. **Remove write permissions for the user's home directory (ensuring they are chrooted to the ftp subdirectory):**  
    sudo chmod a-w /home/ftpuser/ftp  

6. **Add the new user to the vsftpd.chroot_list file:**  
    echo "ftpuser" | sudo tee -a /etc/vsftpd.chroot_list  

### **Test Connection**

1. **Create a blank notebook for testing the upload.**
2. **Determine the IP address of your WSL environment:**  
    You can use either of the following commands:  
    ip a  
    <br/>or (if net-tools is installed):  
    sudo apt install net-tools  
    ifconfig  
    <br/>Look for the eth0 interface (or similar) and note the inet address.

## **3\. Testing FTP Connection with Python**

This section demonstrates how to establish an FTP connection using Python.

from ftplib import FTP_TLS  
<br/>\# FTP details  
ftphost = "localhost" # Replace with your FTP IP address if needed  
ftpuser = "ftpuser" # Replace with your FTP username  
ftppass = "password" # Replace with your FTP password  
ftpport = 21  
<br/>try:  
ftp = FTP_TLS()  
ftp.connect(ftphost, ftpport)  
ftp.login(ftpuser, ftppass)  
ftp.prot_p() # Fix for "522 Data connections must be encrypted"  
print("Successfully connected to FTP server.")  
ftp.quit()  
except Exception as e:  
print(f"An error occurred: {e}")  

## **4\. Setting Up Python Development Environment**

This section outlines how to set up a virtual environment for your Python project.

### **Initialization**

1. **Initialize a Git repository (optional but recommended):**  
    git init .  

2. **Create a virtual environment:**  
    python -m venv env  

3. **Create a requirements.txt file listing the project dependencies:**  
    pandas  
    pyarrow  

4. **Activate the virtual environment:**
    - **On Windows:**  
        source env/Scripts/activate  

    - **On Linux/macOS:**  
        source env/bin/activate  

5. **Install the required packages from requirements.txt:**  
    pip install -r requirements.txt  

### **Securing the Credentials**

1. **Edit the activation script for your virtual environment.**
    - **On Windows:** env/Scripts/activate
    - **On Linux/macOS:** env/bin/activate
2. **Add the following set commands at the lower portion of the file (for Windows) or export commands (for Linux/macOS):**  
    **Windows (env/Scripts/activate):**  
    set FTPHOST=your_ftp_ip_address REM Replace with your FTP IP address  
    set FTPUSER=your_ftp_username REM Replace with your FTP username  
    set FTPPASS=your_ftp_password REM Replace with your FTP password  
    set FTPPORT=21  
    <br/>**Linux/macOS (env/bin/activate):**  
    export FTPHOST="your_ftp_ip_address" # Replace with your FTP IP address  
    export FTPUSER="your_ftp_username" # Replace with your FTP username  
    export FTPPASS="your_ftp_password" # Replace with your FTP password  
    export FTPPORT="21"  

3. **Remember to deactivate and reactivate your virtual environment for these changes to take effect.**  
    deactivate  
    source env/Scripts/activate # On Windows  
    source env/bin/activate # On Linux/macOS  

4. **In your Python code (app.py), you can access these environment variables:**  
    import os  
    <br/>ftp_host = os.environ.get("FTPHOST")  
    ftp_user = os.environ.get("FTPUSER")  
    ftp_pass = os.environ.get("FTPPASS")  
    ftp_port = int(os.environ.get("FTPPORT", 21)) # Default to 21 if not set  
    <br/>print(f"FTP Host: {ftp_host}")  
    print(f"FTP User: {ftp_user}")  
    \# ... use these variables for FTP connection  

## **5\. Creating Python Data Pipeline**

This section outlines the creation of the main Python script (app.py) and a configuration file (config.json).

- **app.py**: This file will contain the Python code to:
  - Extract data from the specified web source (e.g., using libraries like requests or Beautiful Soup).
  - Process and transform the extracted data (e.g., using pandas).
  - Establish an FTP connection using the credentials from environment variables.
  - Transfer the processed data to the FTP server.
- **config.json**: This file can be used to store configuration parameters such as:
  - The URL of the web data source.
  - Specific data extraction rules or selectors.
  - The filename for the transferred data on the FTP server.
  - Other relevant settings.

_(The detailed implementation of app.py and the structure of config.json are beyond the scope of the provided notes, as they depend on the specifics of the data source and desired transformation. These files are crucial for the actual data pipeline.)_