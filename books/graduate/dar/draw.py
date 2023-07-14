import os
import sys

script_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_path)

import zipfile
import json
import pdf2image
import numpy as np
from PIL import Image
import cv2
import os


def create_img_env(env_path, pdf_name):
    # Checkout the env
    if not os.path.exists(env_path):
        os.mkdir(env_path)

    # Create the pdf_env
    # Remove the '.pdf'
    if pdf_name.endswith(".pdf") or pdf_name.endswith(".zip"):
        pdf_name = pdf_name[:-4]
    pdf_path_loc = os.path.join(env_path, pdf_name)
    if not os.path.exists(pdf_path_loc):
        os.mkdir(pdf_path_loc)
    return pdf_path_loc


class Draw:
    def draw_rect(self, image, bound, type, PDF_width=598.0, PDF_height=840.0):
        # notice that the adode regard up-right as positive
        # while the opencv regard down-right as positive
        # 1700-2200: 612-792
        # 1653-2339: 598-840
        # 3 triples
        if image.width == 1700 and image.height == 2200:
            PDF_width = 612
            PDF_height = 792
        elif image.width == 1653 and image.height == 2339:
            PDF_width = 598
            PDF_height = 840
        else:
            PDF_width = int((image.width - 1700) / 3) + 612
            PDF_height = int((image.height - 2200) / 3) + 792
        left = int(bound[0] / PDF_width * image.width)
        bottom = int((PDF_height - bound[1]) / PDF_height * image.height)
        right = int(bound[2] / PDF_width * image.width)
        top = int((PDF_height - bound[3]) / PDF_height * image.height)
        pt1 = (left, top)
        pt2 = (right, bottom)

        # red
        color = (0, 0, 255)
        if type == "Title":
            # (cyan)blue
            color = (255, 255, 0)
        elif type == "Table":
            # green
            color = (0, 255, 0)
        elif type == "Figure":
            # blue
            color = (255, 0, 0)
        elif type == "List":
            # yellow
            color = (0, 255, 255)

        thickness = 4
        image_np = np.array(image)
        # print(pt1, pt2)
        # only accept integer as input
        output_image = cv2.rectangle(image_np, pt1, pt2, color, thickness)

        return Image.fromarray(output_image)

    def draw(self, output_zip, origin_pdf_path, pdf_name=""):
        pdf_path = origin_pdf_path.split("/")[-1]
        pdf_path = pdf_path.split("\\")[-1]
        pdf_name = pdf_name if pdf_name != "" else pdf_path[:-4]
        archive = zipfile.ZipFile(output_zip, 'r')
        jsonEntry = archive.open('structuredData.json')
        jsonData = jsonEntry.read()
        data = json.loads(jsonData)

        # convert pdf file to image
        pages = pdf2image.convert_from_path(origin_pdf_path)
        # data have the following format
        # elements--->[Bounds, Page, Path, attribute]
        for element in data["elements"]:
            if "Bounds" not in element:
                continue
            bounds = element["Bounds"]
            page_no = element["Page"]
            path = element["Path"]
            # attribute = element["attributes"]

            # Path can be ended with different types
            if "Title" in path:
                pages[page_no] = self.draw_rect(pages[page_no], bounds, type="Title")
            elif "Figure" in path:
                pages[page_no] = self.draw_rect(pages[page_no], bounds, type="Figure")
            elif "Table" in path:
                pages[page_no] = self.draw_rect(pages[page_no], bounds, type="Table")
            elif "L" in path:
                pages[page_no] = self.draw_rect(pages[page_no], bounds, type="List")
            else:
                pages[page_no] = self.draw_rect(pages[page_no], bounds, type="Text")

        # Create the env
        pdf_draw_path = create_img_env(os.path.join(script_path, "Draw"), pdf_name)
        # output the image
        for no_page, page in enumerate(pages):
            no_page_draw_path = os.path.join(pdf_draw_path, pdf_name + "_Page_" + str(no_page + 1) + ".png")
            cv2.imwrite(
                no_page_draw_path, np.array(page)
            )
        return pdf_draw_path


# draw = Draw()
# draw.draw(os.path.join("extract/sample.zip"), os.path.join("sample.pdf"))