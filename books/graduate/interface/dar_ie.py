import os
import sys

script_path = os.path.dirname(os.path.abspath(__file__))
dar_path = os.path.join(script_path, "../dar")
sys.path.append(dar_path)

from books.graduate.dar.dar import DAR
import pandas as pd


def dump_para_from_excel(filepath):
    excel_file = pd.DataFrame()
    try:
        excel_file = pd.read_excel(filepath)
    except:
        print("the filepath must be a valid .xlsx file")
        sys.exit(1)
    data = excel_file.to_dict(orient="records")
    const_para = "段落"
    result = []
    for item in data:
        if str(item["title"]) and const_para in str(item["title"]):
            if str(item["content"]) != "nan":
                result.append(str(item["content"]))
    return result


# result = dump_para_from_excel("../dar/Excel/sample.xlsx")
# i = 0