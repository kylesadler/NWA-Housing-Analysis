# import pymongo

from util import *
from config import *
from pdf import *

directory_to_pdf = {
    FAYETTEVILLE_NEW_FORMAT_DIR: NewFayettevillePDF,
    FAYETTEVILLE_DIR: July2020FayettevillePDF,
    FAYETTEVILLE_OLD_FORMAT_DIR: OldFayettevillePDF,
}

data = []
for directory, pdf_class in directory_to_pdf.items():
    for path in get_paths(directory):
        a_pdf = pdf_class(path)
        data.extend(a_pdf.parse())

save_to_csv(data, 'output.csv')
