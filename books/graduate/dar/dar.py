import os
import sys

script_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_path)

from extract import Extract
from draw import Draw
from dumpExcel import dump_excel


class DAR:
    def __init__(self):
        self.extract = Extract()
        self.extracted_path = ""
        self.draw = Draw()

    def extract_pdf(self, path):
        out_path = self.extract.extract(path)[0]
        self.extracted_path = out_path
        return out_path

    def draw_pdf(self, path, origin_path):
        if self.extracted_path == "":
            raise FileNotFoundError
        # out_path = self.extracted_path
        out_path = path
        draw_path = self.draw.draw(output_zip=out_path, origin_pdf_path=origin_path)
        print("Draw successfully! The file is under the './Draw' directory")
        return draw_path

    def dump_content(self, path):
        if self.extracted_path == "":
            raise FileNotFoundError
        out_path = self.extracted_path
        path = dump_excel(out_path)
        print("Dump successfully! The file is under the './Excel' directory")
        return path

    def clear(self):
        self.extracted_path = ""
