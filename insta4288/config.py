"""Insta4288 development configuration."""

import pathlib

# Root of this application, useful if it doesn't occupy an entire domain
APPLICATION_ROOT = '/'

# Secret key for encrypting cookies
SECRET_KEY = b'bit\x0c\xccT:RF\xad\x82\xf5B\xfc\xd2(\xe1"\x0f\xcf"\x97\xad\x04'
SESSION_COOKIE_NAME = 'login'

# File Upload to var/uploads/
INSTA4288_ROOT = pathlib.Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = INSTA4288_ROOT/'var'/'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# Database file is var/insta4288.sqlite3
DATABASE_FILENAME = INSTA4288_ROOT/'var'/'insta4288.sqlite3'
