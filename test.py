# import pymongo
import os
from util import *
from config import *
from pdf import *

paths = get_paths(FAYETTEVILLE_OLD_FORMAT_DIR)
# print(paths)
# exit()
# paths = ['/home/kyle/Documents/Housing/files/fayetteville/old_format/june.pdf'] # error
# paths = [os.path.join(FAYETTEVILLE_OLD_FORMAT_DIR, 'march.pdf')]
data = []
# print(paths[0])
for path in paths:
    print(path)
    fay_pdf = OldFayettevillePDF(path)
    data.extend(fay_pdf.parse())

print_data(data)
# save_to_csv(data, 'output2.csv')
