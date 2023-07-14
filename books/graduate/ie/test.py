import os
import zipfile


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


def test_zip(path, target_path):
    with zipfile.ZipFile(path, "r") as zip_ref:
        zip_ref.extractall(target_path)


if __name__ == '__main__':
    path = os.path.join("../dar/extract/01.zip")
    target_path = create_img_env("../dar/extract", "01.zip")
    test_zip(path, target_path)