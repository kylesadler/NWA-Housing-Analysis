from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox

class PDF:
    def __init__(self, path):
        self.path = path

    def generate_positions(self):
        """ yields a list of text positions for each page in self.path """
        fp = open(self.path, 'rb')
        parser = PDFParser(fp)
        doc = PDFDocument()
        parser.set_document(doc)
        doc.set_parser(parser)
        doc.initialize('')
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        pages = doc.get_pages()

        extra_types = set()

        for page in pages:
            positions = []
            interpreter.process_page(page)
            layout = device.get_result()
            for lobj in layout:
                if isinstance(lobj, LTTextBox):
                    x, y = lobj.bbox[0], lobj.bbox[3]
                    text = lobj.get_text().replace('\n',' ').replace('  ',' ').strip()
                    
                    positions.append({
                        'x':x,
                        'y':y,
                        'text': text.lower(),
                        'original_text': text
                    })
                else:
                    # print(lobj.get_text())
                    # print(repr(lobj))
                    extra_types.add(str(type(lobj)))

            yield positions
        # print(extra_types)
