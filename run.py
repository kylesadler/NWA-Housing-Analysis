# import pymongo

from util import *
from config import *
from pdf import *

data = []
for path in get_paths(FAYETTEVILLE_NEW_FORMAT_DIR):
    fay_pdf = NewFayettevillePDF(path)
    data.extend(fay_pdf.parse())

for path in get_paths(FAYETTEVILLE_DIR):
    fay_pdf = July2020FayettevillePDF(path)
    data.extend(fay_pdf.parse())


save_to_csv(data, 'output2.csv')
