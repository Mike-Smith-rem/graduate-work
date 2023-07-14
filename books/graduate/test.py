import os
import zipfile
import sys
script_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_path)


def create_img_env(pdf_name, env_path=os.path.join(script_path, "dar/extract")):
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


def dump_zip(path, target_path):
    with zipfile.ZipFile(path, "r") as zip_ref:
        zip_ref.extractall(target_path)


def add_directory_to_zip(zip_file, directory_path):
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            zip_file.write(file_path, os.path.relpath(file_path, directory_path))


if __name__ == '__main__':
    path = os.path.join("../dar/extract/01.zip")
    target_path = create_img_env("../dar/extract", "01.zip")
    dump_zip(path, target_path)