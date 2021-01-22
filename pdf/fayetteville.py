import re
from pprint import pprint
# import pymongo

from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from collections import Counter
import logging
from util import *
from config import *

from . import PDF



""" City	Permit Type	Work Class	Permit Number	Value	Contact	Parcel	Address	Square Feet	Apply Date	Issue Date	Expire Date
"""

def add_city(data):
    return ['Fayetteville'] + data

class NewFayettevillePDF(PDF):
    TOLERANCE = 5

    def positions_to_grid(self, positions):
        """ positions list of dicts with keys x,y,text
            (0,0) is bottom left of page
            small y means bottom of page
            returns grid[x][y] with first row titles
        """

        try:
            # try:
            fee_name = get_position(positions, 'fee name')
            # except AssertionError:
            #     choices = [p for p in positions if 'date' in p['text']]
            #     max_x = max(x['x'] for x in choices)
            #     fee_name = [x for x in choices if x['x'] == max_x][0]
            address = get_position(positions, '125 West Mountain Street, Fayetteville, AR 72701')
            # TODO change to page count
            title = get_position(positions, 'PERMIT FEE LISTING BY ISSUED DATE')
            permit_type = get_position(positions, 'permit type')
        except:
            print("formatting has changed")
            pprint(positions)
            raise

        grid_positions = clip(
            positions,
            min_x=permit_type['x'] - self.TOLERANCE, # we want to include permit type
            min_y=address['y'] + self.TOLERANCE,
            max_x=fee_name['x'] - self.TOLERANCE,
            max_y=title['y'] - self.TOLERANCE
            )

        rows = group_rows(grid_positions)

        def is_total_row(r):
            total_in_row = any('total' in x['text'] for x in r)
            valuation_in_row = any('valuation' in x['text'] for x in r)
            return total_in_row and valuation_in_row
        
        # remove totals rows
        rows = [x for x in rows if not is_total_row(x)]

        data_rows = []
        header_row = None
        for row in rows:
            if 'permit type' in [x['text'] for x in row]:
                header_row = row
            else:
                data_rows.append(row)

        assert header_row is not None

        header_row = sort_by(header_row, 'x')
        grid = [[x['text'] for x in header_row]]
        for row in data_rows:
            row = sort_by(row, 'x')
            grid_row = []
            for p in header_row:
                cells = [ x for x in row if within_bounds(x['x'], p['x']-20, p['x']+20) ]
                if len(cells) == 0:
                    grid_row.append('')
                elif len(cells) == 1:
                    grid_row.append(cells[0]['text'])
                else:
                    raise RuntimeError()
                        
            grid.append(grid_row)

        i = [x['text'] for x in header_row].index('valuation')
        j = [x['text'] for x in header_row].index('permit number')
        if any(len(row[i]) == 0 and 'resi' in row[j] for row in grid):
            print(header_row)
            pprint([p for p in grid_positions if '$' in p['text']])
            print(grid)
            raise RuntimeError("grid missing values")
                        
        return grid

    def parse(self):
        """ returns list of tuples (current_permit_type, current_work_class, ...)"""
        current_permit_type = None
        current_work_class = None
        data = []

        for positions in self.generate_positions():
            texts = [p['text'] for p in positions]
            if any('permit issuance summary' in t for t in texts):
                continue # skip summary pages

            grid = self.positions_to_grid(positions)
            for row in grid:
                if 'permit type' in row:
                    assert row.index('permit type') == 0    
                    assert row.index('work class') == 1
                    if 'permit number' in row:  
                        assert row.index('permit number') == 2
                    else:
                        assert row.index('permit') == 2
                    assert row.index('valuation') == 3
                    continue
                
                if len(row[0]) > 0:
                    current_permit_type = row[0]
                
                if len(row[1]) > 0:
                    current_work_class = row[1]

                if current_permit_type == 'residential building permit' and current_work_class in ['new single-family', 'new townhouse']:
                    data_row = [current_permit_type, current_work_class]+row[2:]
                    
                    # remove application, finalization dates
                    data_row = data_row[:-4] + data_row[-3:-2]

                    data.append(data_row)

                assert current_permit_type is not None
                assert current_work_class is not None
                
        return add_city(data)

class OldFayettevillePDF(PDF):
    TOLERANCE = 5

    def in_texts(self, string, texts):
        return any([string in x for x in texts])

    def get_permit_rows(self, positions):
        """ given list of positions (x,y,text dicts), return list of rows (row is a list of positions for the same permit) """


        permits = get_positions(positions, 'permit #')
        num_permits = len(permits)
        assert len(positions) == num_permits * 3

        permits = sort_by(permits, 'y') # sort from low (bottom of page) to high (top)

        rows = []
        for i in range(num_permits):
            try:
                assert i - 1 >= 0
                min_y = permits[i-1]['y']+10 # above previous (lower) permit
            except AssertionError:
                min_y = -100

            max_y = permits[i]['y'] + 10 # top of current permit

            # print(min_y, max_y)

            rows.append(clip(
                positions,
                max_y=max_y,
                min_y=min_y
            ))

        return rows

    def permit_to_data_row(self, permit):
        assert len(permit) == 3
        assert 'permit' in permit[0]['text']
        assert 'building area' in permit[1]['text']
        assert 'valuation' in permit[2]['text']

        # pprint([x for p in permits for x in p])


        return ['1-2 FAMILY', work_type, permit_number, value, contact, parcel, address, square_feet, date]


    def parse(self):
        """ returns list of tuples (current_permit_type, current_work_class, ...)"""
        
        # get pages which have new residential permits
        new_residential_pages = []
        to_append = False
        for i, positions in enumerate(self.generate_positions()):
            original_texts = [p['original_text'] for p in positions]

            if self.in_texts('NEW', original_texts) and self.in_texts('ALTER', original_texts) and self.in_texts('Area this Worktype', original_texts) and not self.in_texts('ADDTN', original_texts):
                to_append = True
            
            if self.in_texts('NEW', original_texts) and self.in_texts('1-2 FAMILY', original_texts) and self.in_texts('Area this Worktype', original_texts):
                new_residential_pages.append(positions)
                break
            
            if to_append:
                new_residential_pages.append(positions)

        # print('new_residential_pages', new_residential_pages)

        data = []
        for i, positions in enumerate(new_residential_pages):
            texts = [p['original_text'] for p in positions]
            print([x for x in texts if "Page" in x])

            if i == 0:
                new = get_position(positions, 'NEW')
            else:
                new = {'y': 1000000}

            try:
                assert i != 0
                total = get_position(positions, 'Area this Worktype')
            except:
                total = {'y': -1}


            page = get_position(positions, 'Page')
            title = get_position(positions, 'Report of Building Permit')

            positions = clip(
                positions,
                max_y=min(new['y'], title['y'])-10,
                min_y=max(page['y'], total['y'])+10
            )

            permits = self.get_permit_rows(positions)
            for p in permits:
                # pprint([x['text'] for x in p])
                data.append(permit_to_data_row(permit))
        
        return add_city(data)

class July2020FayettevillePDF(PDF):
    """ this one is just weird """

    def parse(self):
        data =  [
            ['Residential Building Permit', 'New Single-Family', 'B87520', '$244,675.08', 'JUST RIGHT CONSTRUCTION SERV', '765-26280-000', '1983 E PEPPERVINE DR, FAYETTEVILLE, AR 72701', '1,998', '03/28/2019'],
            ['Residential Building Permit', 'New Single-Family', 'B90716', '$332,968.74', 'COBBLESTONE HOMES', '765-30407-000', '3861 W MACLURA WAY X, FAYETTEVILLE, AR 72704', '2,719', '09/11/2019'],
            ['Residential Building Permit', 'New Single-Family', 'B93462', '$339,472.00', 'CLM HOMES LLC', '765-14971-099', '1315 S DUNCAN AVE, FAYETTEVILLE, AR 72701', '2,800', '02/19/2020'],
            ['Residential Building Permit', 'New Single-Family', 'B94042', '$305,415.24', 'RAUSCH', '765-31402-000', '4600 W HOOVER COLEMAN HOMES LOOP, FAYETTEVILLE, AR 72704', '2,494', '03/24/2020'],
            ['Residential Building Permit', 'New Single-Family', 'B94647', '$410,363.46', 'MARTIN BUILDING GROUP LLC', '765-30327-000', '2284 N WINDSWEPT LN, FAYETTEVILLE, AR 72703', '3,351', '04/27/2020'],
            ['Residential Building Permit', 'New Single-Family', 'B95110', '$207,569.70', 'RAUSCH COLEMAN HOMES', '765-15088-000', '1144 S JAYBIRD LN, FAYETTEVILLE, AR 72701', '1,695', '05/20/2020'],
            ['Residential Building Permit', 'New Single-Family', 'B95520', '$102,499.02', 'DEETER CONSTRUCTION', '765-14501-000', '1623 W MAPLE ST, FAYETTEVILLE, AR 72701', '837', '06/11/2020'],
            ['Residential Building Permit', 'New Single-Family', 'B95744', '$265,493.28', 'SOUTHERN BROTHERS', '765-02588-000', '1394 W CLEVELAND ST, FAYETTEVILLE, AR 72701', '2,168', '06/22/2020'],
            ['Residential Building Permit', 'New Single-Family', 'B95761', '$384,157.02', 'BAUMANN & CROSNO CONSTRUCTION', '765-08618-001', '736 E REBECCA ST, FAYETTEVILLE, AR 72701', '3,137', '06/23/2020'],
            ['Residential Building Permit', 'New Single-Family', 'B95813', '$304,313.10', 'ANDERSON CUSTOM HOMES, LLC', '765-31545-000', '573 N PHOENIX RD, FAYETTEVILLE, AR 72704', '2,485', '06/24/2020'],
            ['Residential Building Permit', 'New Single-Family', 'B95933', '$323,171.94', 'ANDERSON CUSTOM HOMES, LLC', '765-31513-000', '609 N SABINE PASS RD, FAYETTEVILLE, AR 72704', '2,639', '07/02/2020'],
            ['Residential Building Permit', 'New Single-Family', 'B95960', '$304,313.10', 'ANDERSON CUSTOMHOMES, LLC', '765-31578-000', '528 N SABINE PASS RD, FAYETTEVILLE, AR 72704', '2,485', '07/06/2020'],
            ['Residential Building Permit', 'New Single-Family', 'B95962', '$225,081.48', 'RIVERWOOD HOMES LLC', '765-31691-000', '37 S GERANIUM LN, FAYETTEVILLE, AR 72704', '1,838', '07/06/2020'],
            ['Residential Building Permit', 'New Single-Family', 'B95970', '$663,855.66', 'COBBLESTONE HOMES', '765-30384-000', '210 N AINSLEY LOOP, FAYETTEVILLE, AR 72704', '5,421', '07/06/2020'],
            ['Residential Building Permit', 'New Single-Family', 'B95983', '$425,670.96', 'ANDERSON CUSTOM HOMES, LLC', '765-31591-000', '529 N SABINE PASS RD, FAYETTEVILLE, AR 72704', '3,476', '07/07/2020'],
            ['Residential Building Permit', 'New Single-Family', 'B95985', '$311,293.32', 'ANDERSON CUSTOM HOMES, LLC', '765-31577-000', '540 N SABINE PASS RD, FAYETTEVILLE, AR 72704', '2,542', '07/07/2020'],
            ['Residential Building Permit', 'New Single-Family', 'RESI-2020-000006', '$240,633.90', '', '765-31822-000', '892 S JAYBIRD LN, Fayetteville, AR 72701', '1,965', '07/17/2020'],
            ['Residential Building Permit', 'New Single-Family', 'RESI-2020-000007', '$240,633.90', '', '765-31823-000', '870 S JAYBIRD LN, Fayetteville, AR 72701', '1,694', '07/17/2020'],
            ['Residential Building Permit', 'New Single-Family', 'RESI-2020-000008', '$207,447.24', '', '765-31826-000', '804 S JAYBIRD LN, Fayetteville, AR 72701', '1,694', '07/17/2020'],
            ['Residential Building Permit', 'New Single-Family', 'RESI-2020-000035', '$240,633.90', '', '765-15088-000', '958 S KINGFISHER LN, Fayetteville, AR 72701', '1,965', '07/23/2020'],
            ['Residential Building Permit', 'New Single-Family', 'RESI-2020-000036', '$240,633.90', '', '765-31771-000', '942 S KINGFISHER LN, Fayetteville, AR 72701', '1,965', '07/23/2020'],
            ['Residential Building Permit', 'New Single-Family', 'RESI-2020-000037', '$240,633.90', 'RAUSCH COLEMAN HOMES', '765-31772-000', '926 S KINGFISHER LN, Fayetteville, AR 72701', '1,965', '07/24/2020'],
            ['Residential Building Permit', 'New Single-Family', 'RESI-2020-000038', '$240,633.90', 'RAUSCH COLEMAN HOMES', '765-31834-000', '747 S JAYBIRD LN, Fayetteville, AR 72701', '1,965', '07/24/2020'],
            ['Residential Building Permit', 'New Single-Family', 'RESI-2020-000039', '$240,633.90', 'RAUSCH COLEMAN HOMES', '765-31835-000', '761 S JAYBIRD LN, Fayetteville, AR 72701', '1,965', '07/24/2020'],
            ['Residential Building Permit', 'New Single-Family', 'RESI-2020-000040', '$233,286.30', 'RIVERWOOD HOMES,', '765-31694-000', '4571 W TOFINO LN, Fayetteville, AR 72704', '1,905', '07/24/2020'],
            ['Residential Building Permit', 'New Single-Family', 'RESI-2020-000042', '$230,714.64', 'RIVERWOOD HOMES LLC', '765-31679-000', '4461 W BARHEM DR, Fayetteville, AR 72704', '1,884', '07/24/2020'],
            ['Residential Building Permit', 'New Single-Family', 'RESI-2020-000046', '$391,872.00', 'RIGGINS CONSTRUCTION', '765-30705-000', '2251 E ABSOLUTE ST, Fayetteville, AR 72701', '3,200', '07/28/2020']
        ]

        return add_city(data)
