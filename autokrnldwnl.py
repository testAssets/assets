import os
import subprocess
import winreg
import requests
import urllib.request
from bs4 import BeautifulSoup
import re
import ctypes
from tqdm import tqdm
import rarfile
from termcolor import colored

def findIfAvast():
    result = subprocess.run(['sc', 'query', 'Avast'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = result.stdout.decode(errors='ignore',encoding='cp1252')

    if "RUNNING" in output:
        return True
    return False

def getScriptAdminPerm():
    return ctypes.windll.shell32.IsUserAnAdmin()

def disable_avast():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\AVAST Software\Avast', 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(key, 'DisableAntiVirus', 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
        print("Avast Antivirus has been disabled.")
    except WindowsError:
        print("An error occured while trying to disable Avast Antivirus.")

def enable_avast():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\AVAST Software\Avast', 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(key, 'DisableAntiVirus', 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        print("Avast Antivirus has been enabled.")
    except WindowsError:
        print("An error occured while trying to enable Avast Antivirus.")

def getUpdatedKRNLink():
    
    # Find all script tags in the HTML
    response = requests.get("https://wearedevs.net/d/Krnl")

    if response.ok:
        # Get the HTML content of the website
        html_content = response.content

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        scripts = soup.find_all('script')

        # Iterate over the script tags
        for script in scripts:
            # Extract the content inside the script tag
            script_content = script.get_text()

            # Use regular expressions to search for URLs in the script content
            url_matches = re.findall(r'https?://[^\s]+', script_content)
            for url in url_matches:
                if "https://cdnwrd2.com/r" in url:
                    return url.replace(')','').replace("'",'').replace('"','').replace(';','')
    else:
        print(f"Error fetching the knrl website")
        return False

def addWinDefExclusion(folder_path):
    subprocess.run(["powershell.exe", "-Command", f"Add-MpPreference -ExclusionPath '{folder_path}'"])

def avastAVExclusion(folder_path):
    cmd = f"avastcli add-exclusion {folder_path}"

    # Run the command using the subprocess module
    subprocess.run(cmd, shell=True)

    # Check if the exclusion was added successfully
    output = subprocess.run("avastcli list-exclusions", shell=True, capture_output=True)
    if folder_path in output.stdout.decode():
        print("Exclusion added successfully")
    else:
        print("Failed to add exclusion")

os.system("title Krnl Auto Downloader v1 - By notpoiu")

if getScriptAdminPerm() == False:
    print("this script is not run as administrator. please do so or else it wont function properly.")
    os.system("pause")
    exit()

avastExists = findIfAvast()
    
if not avastExists:
    subprocess.run(["powershell.exe", "Set-MpPreference -DisableRealtimeMonitoring $true"])

if avastExists:
    disable_avast()

print("Disabled antivirus program to allow download of krnl")

KrnlDwnlLink = getUpdatedKRNLink()

if not KrnlDwnlLink:
    os.system("pause")
    exit()

# download krnl
def update_progress(count, block_size, total_size):
    pbar.update(count*block_size)

response = urllib.request.urlopen(KrnlDwnlLink)
total_size = int(response.info().get('Content-Length', 0))

with tqdm(total = total_size, unit = "B", unit_scale = True, unit_divisor = 1024) as pbar:
    urllib.request.urlretrieve(KrnlDwnlLink, reporthook=update_progress)

# extract the folder
rar_file = rarfile.RarFile("KRNLWRD.rar")
rar_file.extractall()
rar_file.close()

print(colored("KRNL has successfully been downloaded.", 'green'))

if not avastExists:
    addWinDefExclusion(os.getcwd() + "/KRNLWRD")
    subprocess.run(["powershell.exe", "Set-MpPreference -DisableRealtimeMonitoring $false"])


if avastExists:
    avastAVExclusion(os.getcwd() + "/KRNLWRD")
    enable_avast()

print("Added krnl as a folder exception")
print("reenabled antivirus")

os.system("pause")
exit
