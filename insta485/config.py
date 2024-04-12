"""Insta485 development configuration."""

import pathlib

# Root of this application, useful if it doesn't occupy an entire domain
APPLICATION_ROOT = '/'

# Secret key for encrypting cookies
SECRET_KEY = b")\x07\x88:\x7f+\xb9R\x1f\x16?\
    \x01m\xaa\xb1'\xb7\x04@\x04\x16Z\x1d\x85"
# b'FIXME SET WITH: $ python3 -c "import os; print(os.urandom(24))" '
SESSION_COOKIE_NAME = 'login'

# File Upload to var/uploads/
INSTA485_ROOT = pathlib.Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = INSTA485_ROOT / 'var' / 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# Specify static assets path
static_folder = INSTA485_ROOT / 'insta485' / 'static'
STATIC_URL_PATH = ''

# Database file is var/insta485.sqlite3
DATABASE_FILENAME = INSTA485_ROOT / 'var' / 'insta485.sqlite3'
