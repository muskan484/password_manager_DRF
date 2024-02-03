import re
import os
import json
import base64
import random
import string
import hashlib
import requests
from Crypto.Cipher import AES
from rest_framework import status
from datetime import datetime, timedelta
from rest_framework.response import Response
from password_app.models import PasswordVault

ENCRYPTION_KEY = base64.b64decode(os.environ.get('ENCRYPTION_KEY'))
ENCRYPTION_NONCE = base64.b64decode(os.environ.get('ENCRYPTION_NONCE'))

def check_password_strength(raw_data):
    """
    Check the strength of a password and perform necessary validations.

    Parameters: raw_data (dict): Dictionary containing the raw password.
    Return: raw_data (dict): Dictionary with encrypted password if validation passes.
    Raises: Response: HTTP 400 error with error message if validation fails.
    """
    raw_password =raw_data['password']
    if not len(raw_password) >= 8 and re.search('[A-Z]',raw_password) and re.search('[a-z]',raw_password) and re.search('[0-9]',raw_password) and re.search(r'[~`!@#\$%\^&\*\(\)_\-\+\=\[\]\{\}\:\;\.\?]',raw_password):
        error_message = "Please ensure your password meets the following criteria:\n\nMinimum length of 8 characters.\nCombination of uppercase and lowercase letters.\nAt least one number and one symbol.\nConsider meeting these requirements or utilizing an autogenerated password for enhanced security."
        return Response({"Error":error_message},status=status.HTTP_400_BAD_REQUEST)
    
    if pwned_password(raw_password):
        error_message = "Attention: Your password has been identified in security breaches. Please choose a different, secure password or opt for an automatically generated one for enhanced protection." 
        return Response({"Error":error_message},status=status.HTTP_400_BAD_REQUEST)

    encrypted_password = encrypt_password(raw_password)
    raw_data['password'] = encrypted_password
    return raw_data

def pwned_password(password):
    """
    Check if a password has been exposed in known data breaches.

    Parameters: password (str): Password to check.
    Returns: bool: True if password has been breached, False otherwise.
    """
    sha1_password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = sha1_password[:5], sha1_password[5:]
    response = requests.get(f'https://api.pwnedpasswords.com/range/{prefix}')
    if response.status_code == 200:
        for line in response.text.splitlines():
            if line.startswith(suffix):
                return True
    else:
        print(f"Error: Unable to retrieve data from the Pwned Passwords API. Status code: {response.status_code}")
    return False 

def generate_password():
    """Generates a random password.
     
    Returns: str: Randomly generated password."""
    choices = [string.ascii_letters[:26], string.ascii_letters[26:], string.digits, string.punctuation]
    final_pass = ''
    while len(final_pass)<12:
        for choice in choices:
            final_pass += random.choice(choice)
    return final_pass

def encrypt_password(password):
    """
    Encrypt a password using AES encryption.

    Parameters: password (str): Password to encrypt.
    Returns: str: Encrypted password.
    """
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_CTR, nonce=ENCRYPTION_NONCE)    # Create the AES cipher in CTR mode
    encrypted_password = cipher.encrypt(password.encode('utf-8'))   # Encrypt the password
    encrypted_password_b64 = base64.b64encode(encrypted_password).decode('utf-8')   # Base64 encode the encrypted password and nonce for storage
    return encrypted_password_b64

def decrypt_password(base64_password):
    """
    Decrypt a password using AES decryption.

    Parameters: base64_password (str): Base64 encoded password.
    Returns: str: Decrypted password.
    """
    encrypted_password = base64.b64decode(base64_password)       # Base64 decode the encrypted password and nonce
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_CTR, nonce=ENCRYPTION_NONCE)     # Create the AES cipher in CTR mode
    decrypted_password = cipher.decrypt(encrypted_password).decode('utf-8')     # Decrypt the password
    return decrypted_password

def weekly_report():
    """
    Generate a weekly report of password data.

    Returns: tuple: Tuple containing JSON string of data, last week's date, and today's date.
    """
    today = datetime.now().date()
    last_week = today-timedelta(days=7)
    last_week_data = list(PasswordVault.objects.filter(created_at__date__gte = last_week).values())
    for data in last_week_data:
        data['created_at'] = data['created_at'].strftime("%Y-%m-%d %H:%M:%S")
    return json.dumps(last_week_data), last_week,today