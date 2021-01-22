import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
logging.getLogger("pdfminer").setLevel(logging.ERROR)

REPO_DIR = os.path.abspath(os.path.dirname(__file__))
FILE_DIR = os.path.join(REPO_DIR, 'files')

FAYETTEVILLE_DIR = os.path.join(FILE_DIR, 'fayetteville')
FAYETTEVILLE_NEW_FORMAT_DIR = os.path.join(FAYETTEVILLE_DIR, 'new_format')
FAYETTEVILLE_OLD_FORMAT_DIR = os.path.join(FAYETTEVILLE_DIR, 'old_format')
