import sys
import os
import json
script_path = os.path.dirname(os.path.abspath(__file__))
dar_path = os.path.join(script_path, "dar")
interface_path = os.path.join(script_path, "interface")
ir_path = os.path.join(script_path, "ir")
sys.path.append(script_path)
sys.path.append(dar_path)
sys.path.append(interface_path)
sys.path.append(ir_path)
from dar.dar import DAR
from interface.ie_ir_database import Interface
from ir.local import IR
from interface.dar_ie import dump_para_from_excel
from MyException import MyException


class Graduate:
    def __init__(self):
        self.pdf = ""

        self.dar = DAR()
        self.extract_zip_path = ""
        self.draw_picture_path = ""
        self.dump_excel_path = ""

        self.ie = Interface()
        self.to_be_extracted_text = []
        self.extract_triples = []

        # self.ir = IR()
        # self.query = ""
        # self.answer = ""

    def get_zip_file(self, pdf_path):
        self.pdf = pdf_path
        output_path = self.dar.extract_pdf(pdf_path)
        self.extract_zip_path = output_path
        return output_path

    def get_draw_file(self):
        if self.extract_zip_path == "":
            raise MyException("in main: extract_zip_path is empty")
        output_path = self.dar.draw_pdf(self.extract_zip_path, self.pdf)
        self.draw_picture_path = output_path
        return output_path

    def get_dump_excel(self):
        if self.extract_zip_path == "":
            raise MyException("in main: extract_zip_path is empty")
        self.dump_excel_path = self.dar.dump_content(self.extract_zip_path)
        return self.dump_excel_path

    def orc(self, pdf_path):
        self.pdf = pdf_path
        self.get_zip_file(pdf_path)
        print("ORC1-Extract-Zip-File Successfully! ")
        self.get_draw_file()
        print("ORC2-Draw-Layouts Successfully! ")
        self.get_dump_excel()
        print("ORC3-Dump-Excel Successfully! ")

    def get_to_be_extracted_text(self):
        if self.dump_excel_path == "":
            raise MyException("in main: dump_excel_path is empty")
        result = []
        result = dump_para_from_excel(self.dump_excel_path)
        self.to_be_extracted_text = result
        print("Interface:DAR-IE succeeded! ")

    def get_extract_triples(self, output_path=os.path.join(script_path, "interface/local.json")):
        if len(self.to_be_extracted_text) == 0:
            raise MyException("in main: to_be_extracted_text is empty")
        self.extract_triples = self.ie.transfer_text_to_triples(self.to_be_extracted_text, output_path)
        print("IE-Extract-Triples successfully! ")

    def save_triples(self):
        if len(self.extract_triples) == 0:
            print("IE-IR-Save-Triples Failed, There is no data in extracted triples")
            raise MyException("in main: extract_triples is empty")
        self.ie.save_triple(os.path.join(script_path, "interface/local.json"))
        print("IE-IR-Save-Triples Successfully! ")
        file_name = os.path.join(script_path, "interface/local.json")
        os.remove(file_name)

    def IE_process(self):
        self.get_to_be_extracted_text()
        self.get_extract_triples()
        self.save_triples()

    # def get_answer(self, text):
    #     self.query = text
    #     self.answer = self.ir.read(self.query)
    #     print("IR Successfully! ")
    #     return self.answer

    def clear(self):
        self.pdf = ""

        # self.dar = DAR()
        self.extract_zip_path = ""
        self.draw_picture_path = ""
        self.dump_excel_path = ""
        self.dar.clear()

        # self.ie = Interface()
        self.to_be_extracted_text = []
        self.extract_triples = []
        self.ie.clear()

        # self.ir = IR()
        # self.query = ""
        # self.answer = ""
        # self.ir.clear()


# g = Graduate()
# pdf_path = os.path.join(script_path, "../../files/01.pdf")
# g.orc(pdf_path)
# g.IE_process()
# g.get_answer("心脏病是由什么引起的？")
# print(g.answer)
class IR_problem():
    def __init__(self):
        self.ir = IR()
        self.query = ""
        self.answer = ""

    def get_answer(self, text):
        self.query = text
        self.answer = self.ir.read(self.query)
        print("IR Successfully! ")
        return self.answer
