import logging

from adobe.pdfservices.operation.auth.credentials import Credentials
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.execution_context import ExecutionContext
from adobe.pdfservices.operation.io.file_ref import FileRef
from adobe.pdfservices.operation.pdfops.extract_pdf_operation import ExtractPDFOperation
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_pdf_options import ExtractPDFOptions
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_element_type import ExtractElementType

import os
import sys

script_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_path)

from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_renditions_element_type import \
    ExtractRenditionsElementType
from adobe.pdfservices.operation.pdfops.options.extractpdf.table_structure_type import TableStructureType


class Extract:
    def __init__(self, path_of_api=os.path.join(script_path, "licence/pdfservices-api-credentials.json")):
        try:
            # Initial setup, create credentials instance.
            self.credentials = Credentials.service_account_credentials_builder() \
                .from_file(path_of_api) \
                .build()

            # Create an ExecutionContext using credentials and create a new operation instance.
            self.execution_context = ExecutionContext.create(self.credentials)
            self.extract_pdf_operation = ExtractPDFOperation.create_new()
        except ServiceApiException:
            logging.exception("Exception encountered while executing operation")

    def extract(self, input_file: str, output_zip=os.path.join(script_path, "extract")):
        out_path = []
        if input_file.endswith(".pdf"):
            input_pdf = input_file
            out_path.append(self.__extract_pdf___(input_pdf, output_zip))
        else:
            # 垃圾的批量处理
            for file in os.listdir(os.path.join(input_file)):
                if file.endswith(".pdf"):
                    input_pdf = os.path.join(input_file, file)
                    out_path.append(self.__extract_pdf___(input_pdf, output_zip))
        return out_path

    def __extract_pdf___(self, pdf, output_zip=os.path.join(script_path, "extract")):
        try:
            # Set operation input from a source file.
            print("--------Begin extract pdf-------")
            source = FileRef.create_from_local_file(pdf)
            self.extract_pdf_operation.set_input(source)

            # Build ExtractPDF options and set them into the operation
            extract_pdf_options: ExtractPDFOptions = ExtractPDFOptions.builder() \
                .with_elements_to_extract([ExtractElementType.TEXT, ExtractElementType.TABLES]) \
                .with_elements_to_extract_renditions([ExtractRenditionsElementType.TABLES,
                                                      ExtractRenditionsElementType.FIGURES]) \
                .with_table_structure_format(TableStructureType.CSV) \
                .build()
            self.extract_pdf_operation.set_options(extract_pdf_options)

            # Execute the operation.
            result: FileRef = self.extract_pdf_operation.execute(self.execution_context)

            # Save the result to the specified location.
            pdf = pdf.split("/")[-1]
            pdf = pdf.split("\\")[-1]
            out_path = os.path.join(output_zip, pdf[:-4] + ".zip")
            print("--------output path is ----------" + out_path)
            if os.path.isfile(out_path):
                os.remove(out_path)
            result.save_as(out_path)

            print("Successfully extracted information from PDF.\n")
            return out_path

        except (ServiceApiException, ServiceUsageException, SdkException):
            logging.exception("Exception encountered while executing operation")


# #
# file = "01.pdf"
# extract = Extract()
# extract.extract(file)
