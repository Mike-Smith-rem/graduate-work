import os.path
import zipfile
import json
from pandas import DataFrame
from draw import create_img_env
import sys
script_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_path)

save_dict = {}


def visualize_json(file_zip: str):
    archive = zipfile.ZipFile(file_zip, "r")
    jsonEntry = archive.open('structuredData.json')
    jsonData = jsonEntry.read()
    data = json.loads(jsonData)
    with open(os.path.join(script_path, "Excel", file_zip[:-4] + ".json"), "w", encoding="utf8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    return data


def trans_json_to_mid_format(data: dict):
    current_sect = 0
    current_h = 0
    for element in data["elements"]:
        page = element["Page"]

        # path: //Document/Sect[]/type
        path = str(element["Path"])
        index = path.find("Sect")
        path = path[index:]

        paths = path.split("/")
        # sect_num: 'sect[?]'
        sect_num = paths[0]

        # the type: figure[], l, h?, p, table, title
        category = paths[1]

        # first filter the sect_num
        index_sect_num = 0
        try:
            index_sect_num = sect_num[5: -1]
            if index_sect_num == '':
                index_sect_num = 1
            else:
                index_sect_num = int(index_sect_num) - 1
            current_sect = index_sect_num
        except Exception:
            print(f"There must be error in your string index_sect_num: {index_sect_num}")

        # some specific condition
        # if sect_num == 0, it must be title
        # notice that H appears before P
        """
        Sect{
                "H1": 
                {
                       index: 1
                       text: str,
                       PList: {
                            p1: str
                            p2: str
                       }
                       FigureList: {
                            Figure1: filepaths
                            Figure2: filepaths
                       }
                       LList: {
                            L[1]: {
                                lbody1:
                                lbody2:
                            }
                       }
                       TableList: {
                            Table1: filepaths
                            Table2: filepaths
                       } 
                }
                "H2": 
                {}
            }
        """
        # create new item
        common_item = \
            {
                "index": current_h,
                "text": "",
                "PList": [],
                "FigureList": [],
                "LList": {},
                "TableList": []
            }
        item = {
            "State": "H1",
            "Title": "",
            "H1": common_item,
            "H2": []
        }
        if current_sect in save_dict.keys():
            item = save_dict[current_sect]
        else:
            save_dict[current_sect] = item
            current_h = 0

        # judging process
        # first judging the special one
        if current_sect == 1 and category.startswith("Title"):
            item["Title"] = element["Text"]

        # then the common items
        elif category.startswith("H"):
            if category.startswith("H1"):
                item["State"] = "H1"
                item["H1"]["text"] = element["Text"]
            elif category.startswith("H2"):
                current_h += 1
                h2 = {
                    "index": current_h,
                    "text": element["Text"],
                    "PList": [],
                    "FigureList": [],
                    "LList": {},
                    "TableList": []
                }
                item["H2"].append(h2)
                item["State"] = "H2"
            else:
                print(f"ignore item:{item}")
            continue

        state = item["State"]
        if category.startswith("P"):
            item[state]["PList"].append(element["Text"])

        elif category.startswith("Figure"):
            item[state]["FigureList"].append(element["filePaths"])

        elif category.startswith("L"):
            list_item = paths[2]
            list_item_category = paths[3]
            list_item_dump = []
            if category in item[state]["LList"]:
                list_item_dump = item[state]["LList"][category]
            else:
                item[state]["LList"][category] = list_item_dump
            if list_item_category == "LBody":
                list_item_dump.append(element["Text"])

        elif category.startswith("Table"):
            if "filePaths" in element.keys():
                item[state]["TableList"].append(",".join(element["filePaths"]))


# define the output method
def trans_mid_format_to_excel(dump_item):
    """
    :param dump_item:
                item = {
                    "State": "H1",
                    "Title": "",
                    "H1": common_item,
                    "H2": []
                }
                common_item = \
                {
                    "index": int,
                    "text": "",
                    "PList": [],
                    "FigureList": [],
                    "LList": {},
                    "TableList": []
                }
    :return: {title: str,  content: (文本, 列表, 表格, 图片)}
    """
    json_data = []
    for num, it in enumerate(dump_item.values()):
        if it["Title"] != "":
            json_item = \
                {"title": "标题", "content": it["Title"]}
            json_data.append(json_item)
            # it_h1 = it["H1"]
            # load_h(it_h1, json_data, num)
            # continue

        json_data = load_h(it["H1"], json_data, num + 1)
        """
            for the reason that there seldom contains h2, so h1 is enough
        """
        it_h2 = it["H2"]
        if len(it_h2) != 0:
            for inner_num, h2_list in enumerate(it_h2):
                title_name = "段落" + str(num) + "." + str(inner_num + 1)
                json_item = \
                    {"title": title_name, "content": h2_list["text"]}
                json_data.append(json_item)
                if len(h2_list["PList"]) != 0:
                    json_item = \
                        {"title": "", "content": "\n".join(h2_list["PList"])}
                    json_data.append(json_item)
                if len(h2_list["LList"]) != 0:
                    for num_list, li in enumerate(h2_list["LList"].keys()):
                        li_title = "列表" + str(num_list + 1) + "\n"
                        li_content = "\n".join(h2_list["LList"][li])
                        final_li = li_title + ":" + li_content
                        json_item = \
                            {"title": "", "content": final_li}
                        json_data.append(json_item)
                if len(h2_list["TableList"]) != 0:
                    pass
                if len(h2_list["FigureList"]) != 0:
                    pass

    return json_data


def load_h(it_h1: dict, json_data: list, num: int):
    """
    :param it_h1:
    :param json_data:
    :param num:
    :return:
    """
    if it_h1["text"] or it_h1["PList"] or it_h1["LList"]:
        title_name = "段落" + str(num)
        json_item = \
            {"title": title_name, "content": it_h1["text"]}
        json_data.append(json_item)
        if len(it_h1["PList"]) != 0:
            for index, paragraph in enumerate(it_h1["PList"]):
                json_item = \
                    {"title": title_name + "." + str(index + 1), "content": paragraph}
                json_data.append(json_item)
        if len(it_h1["LList"]) != 0:
            for num_list, li in enumerate(it_h1["LList"].keys()):
                li_title = "列表" + str(num_list + 1)
                li_content = "\n".join(it_h1["LList"][li])
                final_li = li_title + ":" + li_content
                json_item = \
                    {"title": "", "content": final_li}
                json_data.append(json_item)
        if len(it_h1["TableList"]) != 0:
            pass
        if len(it_h1["FigureList"]) != 0:
            pass
    return json_data


def clear():
    global save_dict
    save_dict = {}


# print(save_dict)
def dump_excel(path: str, output=os.path.join(script_path, "Excel")):
    """
    :param path: zip_file_path
    :param output:  output_env
    :return:
    """
    final_json = visualize_json(os.path.join(path))
    trans_json_to_mid_format(final_json)
    final_data = trans_mid_format_to_excel(save_dict)
    title_list = [i["title"] for i in final_data]
    content_list = [i["content"] for i in final_data]

    to_excel_data = DataFrame({"title": title_list, "content": content_list})
    path = path.split("\\")[-1]
    path = path.split("/")[-1]
    # create_img_env("Excel", "")
    to_excel_data.to_excel(os.path.join(output, path[:-4] + ".xlsx"), index=False, encoding="utf8")
    clear()
    return os.path.join(output, path[:-4] + ".xlsx")

# file = "./extract/sample.zip"
# dump_excel(file)