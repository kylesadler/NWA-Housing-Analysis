import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
logging.getLogger("pdfminer").setLevel(logging.ERROR)


FILE_DIR = '/home/kyle/Documents/Housing/files'

FAYETTEVILLE_DIR = os.path.join(FILE_DIR, 'fayetteville')
FAYETTEVILLE_NEW_FORMAT_DIR = os.path.join(FAYETTEVILLE_DIR, 'new_format')
FAYETTEVILLE_OLD_FORMAT_DIR = os.path.join(FAYETTEVILLE_DIR, 'old_format')
